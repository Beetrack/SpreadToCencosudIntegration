import json, os
from pkg.paris_handler import ParisHandler
from pkg.beetrack_api import BeetrackAPI
from pkg.commons import fetch_tag_value

def integrate(event, context):
  print(event)
  body = json.loads(event['body'])
  print(body)
  paris = ParisHandler(body)
  
  if (body.get("resource") == "route" and body.get("event") == "start"):
    print({"Handler If Case" : "Start Route"})
    route_id = body.get("route")
    route_start_at = body.get("started_at")
    spread_route = BeetrackAPI(os.environ.get("paris_api_key")).get_route(route_id)

    if not spread_route:
      print("Route does not exist or doesn't have any Paris dispatch.")
      response_body = {"message": "Route does not exist or doesnt have Paris dispatches"}

    else:
      truck_identifier = "SPR-" + body.get("truck")
      verify_truck = paris.check_or_create_trucks(truck_identifier)
      print(verify_truck)
      get_paris_dispatches = paris.create_paris_dispatches(spread_route)
      print(get_paris_dispatches)
      create_route_on_paris = paris.create_new_route(verify_truck, get_paris_dispatches)
      print(create_route_on_paris)
      new_paris_route_id = create_route_on_paris.get('response').get('route_id')
      print(new_paris_route_id)
      start_paris_route = paris.start_route(new_paris_route_id, route_start_at)
      print(start_paris_route)
      response_body = {"Message": "Route was created and Started correctly"}

  elif body.get("resource") == "dispatch" and body.get("event") == "update":
    print({"Handler If Case" : "Update Dispatch"})
    group_name = fetch_tag_value(body.get("groups"), "name")
    if group_name == "PARIS" and body.get("status") != 1:
      update_dispatch_on_paris = paris.update_dispatch()
      print(update_dispatch_on_paris)
      response_body = {"Message": "Dispatch was updated with new status"}
    else:
      response_body = {"Message": "Resource is dispatch but event is not update or is not Paris group or status is pending. Not doing anything."}

  else:
    response_body = {"Message': 'Webhook resource is not 'route' or 'dispatch'. Not doing anything"}

  response = {
          "statusCode": 200,
          "body": response_body
      }
  print({"Response Body": response_body})
  return response
