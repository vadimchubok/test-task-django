import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from db.models import Table, Booking


@method_decorator(csrf_exempt, name="dispatch")
class BookingView(View):
    """
    GET: return all tables
    GET + querry param: returns a list of available tables for a given date ± 2 hours. "date": "01.07.2023T20:00"

    POST: Create new booking
    """


    def get(self, request):
        date_param = request.GET.get("date")
        tables = Table.objects.all()

        if date_param:
            try:
                date = datetime.strptime(date_param, "%d.%m.%YT%H:%M")
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            start = date - timedelta(hours=2)
            end = date + timedelta(hours=2)

            booked_tables = Booking.objects.filter(
                date__range=(start, end)
            ).values_list("table_id", flat=True)

            tables = tables.exclude(id__in=booked_tables)

        return JsonResponse(
            {"tables": [{"id": t.id, "name": t.name} for t in tables]}
        )

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        client_name = data.get("client_name")
        client_phone = data.get("client_phone")
        table_id = data.get("table")
        date_str = data.get("date")

        if not all([client_name, client_phone, table_id, date_str]):
            return JsonResponse({"error": "Missing fields"}, status=400)

        try:
            date = datetime.strptime(date_str, "%d.%m.%YT%H:%M")
        except ValueError:
            return JsonResponse({"error": "Invalid date format"}, status=400)

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return JsonResponse({"error": "Table not found"}, status=404)

        start = date - timedelta(hours=2)
        end = date + timedelta(hours=2)

        conflict = Booking.objects.filter(
            table=table,
            date__range=(start, end)
        ).exists()

        if conflict:
            return JsonResponse(
                {"error": "Table already booked in this time range"},
                status=409,
            )

        booking = Booking.objects.create(
            table=table,
            date=date,
            client_name=client_name,
            client_phone=client_phone,
        )

        return JsonResponse(
            {
                "id": booking.id,
                "client_name": booking.client_name,
                "client_phone": booking.client_phone,
                "date": booking.date,
                "table": booking.table.id,
            },
            status=201,
        )
