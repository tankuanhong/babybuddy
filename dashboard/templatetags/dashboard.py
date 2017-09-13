# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils import timezone

from core.models import DiaperChange, Feeding, Sleep, TummyTime


register = template.Library()


@register.inclusion_tag('cards/feeding_last.html')
def card_feeding_last(child):
    """Information about the most recent feeding.
    """
    instance = Feeding.objects.filter(child=child).order_by('-end').first()
    return {'feeding': instance}


@register.inclusion_tag('cards/feeding_last_method.html')
def card_feeding_last_method(child):
    """Information about the most recent feeding _method_.
    """
    instance = Feeding.objects.filter(child=child).order_by('-end').first()
    return {'feeding': instance}


@register.inclusion_tag('cards/diaperchange_last.html')
def card_diaperchange_last(child):
    """Information about the most recent diaper change.
    """
    instance = DiaperChange.objects.filter(
        child=child).order_by('-time').first()
    return {'change': instance}


@register.inclusion_tag('cards/diaperchange_types.html')
def card_diaperchange_types(child):
    """Diaper change statistics for the last seven days including today.
    """
    stats = {}
    max_date = (timezone.localtime() + timezone.timedelta(
        days=1)).replace(hour=0, minute=0, second=0)
    min_date = (max_date - timezone.timedelta(
        days=6)).replace(hour=0, minute=0, second=0)

    for x in range(6):
        stats[x] = {'wet': 0, 'solid': 0}

    instances = DiaperChange.objects.filter(child=child)\
        .filter(time__gt=min_date).filter(time__lt=max_date).order_by('-time')
    for instance in instances:
        key = (max_date - instance.time).days
        if instance.wet:
            stats[key]['wet'] += 1
        if instance.solid:
            stats[key]['solid'] += 1

    for key, info in stats.items():
        total = info['wet'] + info['solid']
        if total > 0:
            stats[key]['wet_pct'] = info['wet'] / total * 100
            stats[key]['solid_pct'] = info['solid'] / total * 100

    return {'stats': stats, 'last_change': instances.first()}


@register.inclusion_tag('cards/tummytime_last.html')
def card_tummytime_last(child):
    """Information about the most recent tummy time.
    """
    instance = TummyTime.objects.filter(child=child).order_by('-end').first()
    return {'tummytime': instance}


@register.inclusion_tag('cards/tummytime_day.html')
def card_tummytime_day(child, date=None):
    """Tummy time over the course of `date`.
    """
    if not date:
        date = timezone.localtime().date()
    instances = TummyTime.objects.filter(
        child=child, end__day=date.day).order_by('-end')
    stats = {
        'total': timezone.timedelta(seconds=0),
        'count': instances.count()
    }
    for instance in instances:
        stats['total'] += timezone.timedelta(
            seconds=instance.duration_td().seconds)
    return {'stats': stats, 'instances': instances, 'last': instances.first()}


@register.inclusion_tag('cards/sleep_last.html')
def card_sleep_last(child):
    """Information about the most recent sleep entry.
    """
    instance = Sleep.objects.filter(child=child).order_by('-end').first()
    return {'sleep': instance}


@register.inclusion_tag('cards/sleep_day.html')
def card_sleep_day(child, date=None):
    """Total sleep time for a child on the current day.
    """
    if not date:
        date = timezone.localtime().date()
    instances = Sleep.objects.filter(child=child).filter(start__day=date.day) \
        | Sleep.objects.filter(child=child).filter(end__day=date.day)

    total = timezone.timedelta(seconds=0)
    for instance in instances:
        start = timezone.localtime(instance.start)
        end = timezone.localtime(instance.end)
        # Account for dates crossing midnight.
        if start.date() != date:
            start = start.replace(day=end.day, hour=0, minute=0, second=0)
        elif end.date() != date:
            end = start.replace(day=start.day, hour=23, minute=59, second=59)

        total += end - start

    return {
        'total': total,
        'count': len(instances),
        'average': total/len(instances)
    }
