from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from .models import Component


def component_list(request):
    qs = Component.objects.select_related('spec').all()

    # Фільтрація
    type_filter  = request.GET.get('type', '')
    brand_filters = [brand.strip() for brand in request.GET.getlist('brand') if brand.strip()]
    price_min    = request.GET.get('price_min', '')
    price_max    = request.GET.get('price_max', '')
    search       = request.GET.get('q', '')

    if type_filter:
        qs = qs.filter(type=type_filter)
    if brand_filters:
        qs = qs.filter(brand__in=brand_filters)
    def parse_decimal(raw_value):
        if not raw_value:
            return None
        try:
            return Decimal(str(raw_value))
        except (InvalidOperation, ValueError):
            return None

    parsed_price_min = parse_decimal(price_min)
    parsed_price_max = parse_decimal(price_max)

    if parsed_price_min is not None:
        qs = qs.filter(price__gte=parsed_price_min)
    if parsed_price_max is not None:
        qs = qs.filter(price__lte=parsed_price_max)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(brand__icontains=search))

    # Сортування
    sort = request.GET.get('sort', 'price')
    allowed_sorts = {'name', '-name', 'price', '-price'}
    if sort in allowed_sorts:
        qs = qs.order_by(sort)

    # Пагінація
    paginator = Paginator(qs, 12)
    page = request.GET.get('page', 1)
    components = paginator.get_page(page)

    brands = Component.objects.values_list('brand', flat=True).distinct().order_by('brand')

    from django.db.models import Min, Max
    price_bounds = Component.objects.aggregate(mn=Min('price'), mx=Max('price'))
    price_abs_min = int(price_bounds['mn'] or 0)
    price_abs_max = int(price_bounds['mx'] or 999999)

    context = {
        'components':   components,
        'brands':       brands,
        'component_types': Component.Type.choices,
        'current_type':  type_filter,
        'current_brands': brand_filters,
        'current_sort':  sort,
        'price_min':     price_min,
        'price_max':     price_max,
        'search':        search,
        'price_abs_min': price_abs_min,
        'price_abs_max': price_abs_max,
    }
    return render(request, 'catalog/list.html', context)


def component_detail(request, pk):
    component = get_object_or_404(Component.objects.select_related('spec'), pk=pk)
    context = {'component': component, 'spec': getattr(component, 'spec', None)}
    return render(request, 'catalog/detail.html', context)
