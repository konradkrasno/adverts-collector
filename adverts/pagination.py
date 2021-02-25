from typing import *

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(objects: List, page: int, per_page: int) -> List:
    paginator = Paginator(objects, per_page)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects
