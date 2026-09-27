from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta

from .models import Note


def home(request):
    """
    Main dashboard view.
    Handles note listing, search, category filter, sorting, favorites,
    pagination, and dashboard statistics.
    """
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    sort_option = request.GET.get('sort', 'newest').strip()
    favorite_filter = request.GET.get('favorite', '').strip()

    # Base queryset
    notes_qs = Note.objects.all()

    # Apply search filter (title or content)
    if search_query:
        notes_qs = notes_qs.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Apply category filter
    if category_filter and category_filter != 'All':
        notes_qs = notes_qs.filter(category=category_filter)

    # Apply favorites filter
    if favorite_filter in ['1', 'true', 'True']:
        notes_qs = notes_qs.filter(is_favorite=True)

    # Apply sorting
    if sort_option == 'oldest':
        notes_qs = notes_qs.order_by('created_at')
    elif sort_option == 'title_asc':
        notes_qs = notes_qs.order_by('title')
    elif sort_option == 'title_desc':
        notes_qs = notes_qs.order_by('-title')
    elif sort_option == 'updated':
        notes_qs = notes_qs.order_by('-updated_at')
    else:  # newest
        notes_qs = notes_qs.order_by('-created_at')
        sort_option = 'newest'

    # Filtered count vs total
    filtered_count = notes_qs.count()

    # Pagination: 6 notes per page
    paginator = Paginator(notes_qs, 6)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    # Dashboard Statistics (computed from entire database)
    all_notes = Note.objects.all()
    total_notes = all_notes.count()
    study_count = all_notes.filter(category='Study').count()
    project_count = all_notes.filter(category='Project').count()
    personal_count = all_notes.filter(category='Personal').count()
    work_count = all_notes.filter(category='Work').count()
    other_count = all_notes.filter(category='Other').count()
    favorites_count = all_notes.filter(is_favorite=True).count()

    # Distinct categories present in database
    categories_in_db = set(all_notes.values_list('category', flat=True))
    total_categories = len(categories_in_db) if categories_in_db else 0

    # Notes created in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_created_count = all_notes.filter(created_at__gte=seven_days_ago).count()

    # Recent 5 notes for the sidebar / quick peek widget
    recent_notes = all_notes.order_by('-created_at')[:5]

    # Category choices defined in model
    category_choices = [c[0] for c in Note.CATEGORY_CHOICES]

    # Check if any active filters are applied
    has_active_filters = bool(
        search_query or
        (category_filter and category_filter != 'All') or
        favorite_filter in ['1', 'true', 'True'] or
        sort_option != 'newest'
    )

    # Build query string for pagination links (excluding page parameter)
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'notes': page_obj,
        'page_obj': page_obj,
        'search': search_query,
        'category': category_filter,
        'sort': sort_option,
        'favorite': favorite_filter,
        'filtered_count': filtered_count,
        'has_active_filters': has_active_filters,
        'querystring': querystring,

        # Statistics
        'total_notes': total_notes,
        'study_count': study_count,
        'project_count': project_count,
        'personal_count': personal_count,
        'work_count': work_count,
        'other_count': other_count,
        'favorites_count': favorites_count,
        'total_categories': total_categories,
        'recent_created_count': recent_created_count,
        'recent_notes': recent_notes,
        'category_choices': category_choices,
    }

    return render(request, 'notes/home.html', context)


def add_note(request):
    """
    Creates a new note with validation, word count, and category choices.
    """
    category_choices = [c[0] for c in Note.CATEGORY_CHOICES]

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'Other').strip()
        is_favorite = 'is_favorite' in request.POST

        # Validation
        errors = False
        if not title:
            messages.error(request, 'Please provide a title for your note.')
            errors = True
        elif len(title) > 200:
            messages.error(request, 'Title cannot exceed 200 characters.')
            errors = True

        if not content:
            messages.error(request, 'Note content cannot be empty.')
            errors = True

        if errors:
            return render(request, 'notes/add_note.html', {
                'title': title,
                'content': content,
                'category': category,
                'is_favorite': is_favorite,
                'category_choices': category_choices,
            })

        note = Note.objects.create(
            title=title,
            content=content,
            category=category,
            is_favorite=is_favorite
        )
        messages.success(request, f'Note "{note.title}" created successfully!')
        return redirect('home')

    return render(request, 'notes/add_note.html', {
        'category_choices': category_choices
    })


def view_note(request, id):
    """
    Renders note detail or returns JSON for AJAX modal requests.
    """
    note = get_object_or_404(Note, id=id)

    # Support JSON requests for dynamic modals
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json'
    if is_ajax:
        return JsonResponse({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'category': note.category,
            'is_favorite': note.is_favorite,
            'created_at': note.created_at.strftime("%b %d, %Y, %I:%M %p"),
            'updated_at': note.updated_at.strftime("%b %d, %Y, %I:%M %p"),
            'word_count': note.word_count,
            'char_count': note.char_count,
            'reading_time': note.reading_time,
        })

    return render(request, 'notes/view_note.html', {'note': note})


def edit_note(request, id):
    """
    Modifies an existing note with live validation and field pre-population.
    """
    note = get_object_or_404(Note, id=id)
    category_choices = [c[0] for c in Note.CATEGORY_CHOICES]

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'Other').strip()
        is_favorite = 'is_favorite' in request.POST

        # Validation
        if not title:
            messages.error(request, 'Title cannot be blank.')
            return render(request, 'notes/edit_note.html', {
                'note': note,
                'category_choices': category_choices,
                'form_title': title,
                'form_content': content,
                'form_category': category,
                'form_is_favorite': is_favorite
            })

        if not content:
            messages.error(request, 'Note content cannot be blank.')
            return render(request, 'notes/edit_note.html', {
                'note': note,
                'category_choices': category_choices,
                'form_title': title,
                'form_content': content,
                'form_category': category,
                'form_is_favorite': is_favorite
            })

        note.title = title
        note.content = content
        note.category = category
        note.is_favorite = is_favorite
        note.save()

        messages.success(request, f'Note "{note.title}" updated successfully!')
        return redirect('home')

    return render(request, 'notes/edit_note.html', {
        'note': note,
        'category_choices': category_choices
    })


def delete_note(request, id):
    """
    Deletes the note safely and displays a success notification.
    """
    note = get_object_or_404(Note, id=id)
    title = note.title
    note.delete()
    messages.success(request, f'Note "{title}" deleted successfully!')
    return redirect('home')


def toggle_favorite(request, id):
    """
    Toggles the is_favorite state of a note.
    Supports both AJAX and standard HTTP redirection.
    """
    note = get_object_or_404(Note, id=id)
    note.is_favorite = not note.is_favorite
    note.save()

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json'
    if is_ajax:
        return JsonResponse({
            'success': True,
            'id': note.id,
            'is_favorite': note.is_favorite,
            'title': note.title,
            'message': f'"{note.title}" {"added to" if note.is_favorite else "removed from"} favorites.'
        })

    action = 'added to' if note.is_favorite else 'removed from'
    messages.success(request, f'Note "{note.title}" {action} favorites.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('home')