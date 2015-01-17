import datetime
from datetime import timedelta
import re
import time
import json

from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from Course.models import Course
from Slides.models import Lecture, Slide, Stream
from Slides.settings import LIVECAST_START
from Slides.settings import SLIDE_SECRET

"""
- slidecasting_mode
sets the state of the contentbar (which is included in all templates 
that are used by slidecasting), it has one of the following values:
    * 'start'
    * 'livecast'
    * 'studio'
    * 'new_comments_since'
    * 'marked_slides'
    * 'exercises'
    * 'discourses'
    * 'search_results'
    * 'create_pdf'
    
- tags
the following tags can be attached to slides:
    * .preparation
    * .exercise
"""


def start(request, course_short_title=None):
    course = Course.get_or_raise_404(course_short_title)
    lectures = _get_contentbar_data(course)
    render_dict = {'slidecasting_mode': 'start', 'course': course, 'lectures': lectures}
    return render_to_response('start.html', render_dict, context_instance=RequestContext(request))


@csrf_exempt
def livecast_new_slide(request, course_short_title=None):
    if not request.method == 'POST' or not request.POST['secret'] == SLIDE_SECRET:
        return HttpResponse('must post')

    try:
        now = datetime.datetime.now()
        course = Course.get_or_raise_404(course_short_title)
        if 'lecture_id' in request.POST:
            lecture = Lecture.objects.get(course=course, active=True, id=request.POST['lecture_id'])
            tags = ''
        else:
            if _livecast_now(course):
                lecture = Lecture.objects.get(start__lte=now, end__gte=now, course=course, active=True)
                tags = ""
            else:
                lecture = Lecture.objects.filter(end__gte=now, course=course, active=True).order_by('start')[0]
                tags = ".preparation"

        if 'pub_date' in request.POST:
            pub_date = datetime.datetime.fromtimestamp(int(request.POST['pub_date']))
        else:
            pub_date = now

        slide = Slide(title=request.POST['title'], pub_date=pub_date, filename=request.POST['filename'],
                      lecture=lecture, tags=tags)
        slide.save()
        return HttpResponse(str(slide.id))
    except ValueError:
        return HttpResponse('time error')
    except (Course.DoesNotExist, Course.MultipleObjectsReturned):
        return HttpResponse('course error.')
    except (Lecture.DoesNotExist, Lecture.MultipleObjectsReturned, IndexError):
        return HttpResponse('lecture error.')


def livecast_update_slide(request, course_short_title=None, client_timestamp=None):
    course = Course.get_or_raise_404(course_short_title)
    client_time = datetime.datetime.fromtimestamp(int(client_timestamp))
    slides = Slide.objects.filter(lecture__course=course, lecture__active=True, pub_date__gte=client_time)
    if slides.count() > 0:
        json_response = {'update': True, 'slide_id': slides.reverse()[0].id}
    else: 
        json_response = {'update': False}
    json_response.update({'last_update': int(time.time())})
    return HttpResponse(json.dumps(json_response), content_type='application/javascript')


def livecast(request, lecture_id=None, course_short_title=None):
    course = Course.get_or_raise_404(course_short_title)
    lectures = _get_contentbar_data(course)
    lecture = get_object_or_404(Lecture, id=lecture_id, course=course, active=True)
    if not _livecast_now(lecture):
        url = reverse('Slides:studio_lecture', args=(course_short_title, lecture_id))
        return redirect(url)

    update_slides_url = reverse('Slides:livecast_update_slide', args=(course_short_title, 0))
    # the last part of the url, i.e. the timestamp, should be set by js so should be removed
    # from the base url js gets for using
    update_slides_url = re.sub('0/$', '', update_slides_url)
    render_dict = {'slidecasting_mode': 'livecast', 'course': course, 'lectures': lectures,
                   'lecture': lecture, 'last_update': int(time.time()), 'update_slides_url': update_slides_url}
    return render_to_response('livecast.html', render_dict, context_instance=RequestContext(request))


def studio_lecture(request, course_short_title=None, lecture_id=None):
    course = Course.get_or_raise_404(course_short_title)
    user = RequestContext(request)['user']
    lectures = _get_contentbar_data(course)
    lecture = get_object_or_404(Lecture, id=lecture_id, course=course, active=True)
    if _livecast_now(lecture):
        url = reverse('Slides:livecast', args=(course_short_title, lecture_id)) + lecture_id
        return redirect(url)
    slides = Slide.objects.filter(lecture=lecture)
    slides = _cache_slide_markers(slides)
    slides_preparation = slides.filter(tags__contains='.preparation')
    slides_preparation = _cache_slide_markers(slides_preparation)
    videoclip_url, videoclip_name = _get_videoclip_url_name(lecture)
    videoclip_chapters = _get_videoclip_chapters(lecture, slides, slides_preparation)
    
    render_dict = {'slidecasting_mode': 'studio', 'course': course, 'lectures': lectures, 'lecture': lecture}
    render_dict.update({'slides': slides, 'slides_preparation': slides_preparation, 'user': user})
    render_dict.update({
        'videoclip_name': videoclip_name,
        'videoclip_url': videoclip_url,
        'videoclip_chapters': videoclip_chapters})
    return render_to_response('studio.html', render_dict, context_instance=RequestContext(request))
    

def studio_marker(request, marker, course_short_title=None):
    course = Course.get_or_raise_404(course_short_title)
    user = RequestContext(request)['user']
    lectures = _get_contentbar_data(course)
    if marker == 'confusing':
        slides = Slide.objects.filter(confusing=user, lecture__course=course)
    elif marker == 'important':
        slides = Slide.objects.filter(important=user, lecture__course=course)
    elif marker == 'liked':
        slides = Slide.objects.filter(liked=user, lecture__course=course)
    else:
        raise Http404
    slides = _cache_slide_markers(slides)
    render_dict = {'slidecasting_mode': 'marked_slides', 'marker': marker, 'course': course}
    render_dict.update({'lectures': lectures, 'slides': slides, 'user': user})
    return render_to_response('studio.html', render_dict, context_instance=RequestContext(request))


def studio_search(request, course_short_title=None):
    course = Course.get_or_raise_404(course_short_title)
    lectures = _get_contentbar_data(course)
    search_text = request.GET.get('search_text', '')
    if search_text.strip():
        search_query = _get_query(search_text, ['title', 'tags'])  # TODO: we'll need to search the comments here too.
        slides = Slide.objects.filter(lecture__course=course).filter(search_query).distinct()
        slides = _cache_slide_markers(slides)
        render_dict = {'slidecasting_mode': 'search_results', 'course': course, 'lectures': lectures, 'slides': slides,
                       'search_text': search_text}
        return render_to_response('studio.html', render_dict, context_instance=RequestContext(request))
    else:
        raise Http404


def mark_slide(request, course_short_title=None, slide_id=None, marker=None, value=None):
    user = RequestContext(request)['user']
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'success': False}), content_type='application/javascript')
    try:
        slide = Slide.objects.get(id=slide_id)
    except (Slide.DoesNotExist, Slide.MultipleObjectsReturned):
        return HttpResponse(json.dumps({'success': False}), content_type='application/javascript')
    if value == 'xxx':
        return HttpResponse(json.dumps({'success': False}), content_type='application/javascript')
    elif value == 'true':
        slide.set_marker(user, marker, True)
    else:
        slide.set_marker(user, marker, False)
    count = slide.get_marker_count(marker)
    new_title = render_to_string('marker_title.html', {'count': count, 'marker': marker})
    json_return_dict = {'success': True, 'count': count, 'new_title': new_title}
    return HttpResponse(json.dumps(json_return_dict), content_type='application/javascript')


def _get_contentbar_data(course):
    lectures = Lecture.objects.filter(course=course, active=True)
    return lectures


def _get_videoclip_url_name(lecture):
    try:
        return lecture.stream.url, lecture.stream.clipname
    except Stream.DoesNotExist:
        return "no_url", "no_videoclip"
        
        
def _get_videoclip_chapters(lecture, slides, slides_preparation):
    try:
        offset = lecture.stream.offset
        return [
            [slide.id, 1000 * (offset + (slide.pub_date - lecture.start).seconds)]
            for slide in slides.exclude(id__in=slides_preparation)
        ]
    except Stream.DoesNotExist:
        return []


def _cache_slide_markers(slides):
    # call this function after you have filtered the queryset of slides you want to display.
    # it makes annotations for markers, and prefetches the marker relations. we need
    # both everywhere, where we display slides (because we show the markers everywhere). 
    # this strongly improves performance!
    return slides.annotate(count_confusing=Count('confusing'))\
        .annotate(count_important=Count('important'))\
        .annotate(count_liked=Count('liked'))\
        .prefetch_related('confusing')\
        .prefetch_related('important')\
        .prefetch_related('liked')


def _livecast_now(lecture_or_course):
    now = datetime.datetime.now()
    if type(lecture_or_course) == Lecture:
        lecture = lecture_or_course
        lecture_livecast_start = lecture.start - timedelta(minutes=LIVECAST_START)
        print(lecture_livecast_start)
        print(now)
        print(lecture.end)
        if lecture_livecast_start < now < lecture.end:
            print('true')
            return True
        else:
            return False
    elif type(lecture_or_course) == Course:
        course = lecture_or_course
        lecture_right_now = Lecture.objects.filter(course=course,
                                                   start__lte=(now + timedelta(minutes=LIVECAST_START)),
                                                   end__gte=now, active=True)
        if lecture_right_now.count() == 1:
            return True
        else:
            return False
    else:
        return False
    

def _get_query(query_string, search_fields):
    # Returns a query, that is a combination of Q objects. That combination
    # aims to search keywords within a model by testing the given search fields.
    query = None  # Query to search for every search term
    terms = _normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def _normalize_query(query_string,
                     findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                     normspace=re.compile(r'\s{2,}').sub):
    # Splits the query string in invidual keywords, getting rid of unecessary spaces
    #    and grouping quoted words together.
    #    Example:
    #    
    #    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    #    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    #
    #
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
