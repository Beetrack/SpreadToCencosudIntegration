import json, os
from pkg.paris_handler import ParisHandler
from pkg.spread_handler import SpreadHandler
from pkg.beetrack_api import BeetrackAPI
from pkg.commons import fetch_tag, fetch_tag_value, response_handler

def integrate(event, context):
  print({"Event": event})
  body = json.loads(event['body'])
  print({"Body": body})
  paris = ParisHandler(body)
  spread = SpreadHandler(body)
  account_id_spread = os.environ.get("account_id_spread")
  account_id_paris = os.environ.get("account_id_paris")
  account_id = body.get("account_id")
  resource = body.get("resource")
  event = body.get("event")
  truck = body.get("truck")
  is_trunk = body.get("is_trunk")
  print({"Event from Account ID": account_id})

  paris_trucks = ["SPREAD"]

  if (resource == "route" and event == "update" and account_id == int(account_id_paris) and (truck in paris_trucks)):
    # Clone trunk route for Spread from Paris account to Spread account.
    print({"Handler if case": "Paris Route"})
    paris_route_id = body.get("route")
    print({"Paris Route ID": paris_route_id})
    get_paris_route = BeetrackAPI(os.environ.get("paris_api_key"), "https://app.beetrack.dev/api/external/v1").get_route(paris_route_id) 
    # Cambiar al paso a producción por https://app.beetrack.com/api/external/v1
    print({"Paris Route Information": get_paris_route})
    get_trunk_dispatches = spread.get_spread_trunk_dispatches(get_paris_route)
    print({"Paris Route Trunk Dispatches": get_trunk_dispatches})
    if get_trunk_dispatches == []:
      print("Paris trunk route does not belong to Spread or doesn't have any Spread dispatches.")
      response_body = "Message: Trunk route does not belong to Spread or doesn't have any Spread dispatch."
    else:
      truck_identifier = "PAR-" + body.get("truck")
      print("Paris vehicle in Spread account :", truck_identifier)
      verify_spread_truck = spread.check_or_create_trucks(truck_identifier)
      print("Verify existence Paris truck in Spread account :", verify_spread_truck)
      create_trunk_route_on_spread = spread.create_new_trunk_route(verify_spread_truck, get_trunk_dispatches)
      print("Response after creating a Paris trunk route in Spread :", create_trunk_route_on_spread)
      response_body = response_handler(create_trunk_route_on_spread, "Message: Trunk route was created in Spread")
  
  elif (resource == "dispatch" and event == "update" and account_id == int(account_id_paris) and is_trunk == True and body.get("status") == 1):
    # Get id dispatch of the dispatches of Paris and added to a tag associated to the Spread dispatches.
    print({"Handler If Case" : "Paris Update Dispatch for adding ID Dispatch on Spread Trunks"})
    update_dispatch_id_on_spread = spread.get_id_dispatch_spread()
    response_body = response_handler(update_dispatch_id_on_spread, "Message: Dispatch was updated on Spread with the id dispatch on Paris")

  elif (resource == "dispatch" and event == "update" and account_id == int(account_id_spread) and is_trunk == True):
    # Update trunk dispatch on Paris account.
    print({"Handler If Case" : "Update Trunk Dispatch in Paris"})
    update_trunk_dispatch_on_paris = paris.update_trunk_dispatch()
    response_body = response_handler(update_trunk_dispatch_on_paris, "Message: Dispatch was updated in Paris succesfully with new status")

  elif (resource == "dispatch" and event== "update" and account_id == int(account_id_spread) and is_trunk == False):
    print({"Handler If Case" : "Update Spraed dispatches on Paris"})
    group_name = fetch_tag(body.get("groups"), "name")
    if group_name == "Paris" and (body.get("status") in [1,2,3,4]):
      #Cambiar a Paris cuando se metan las credenciales de Spread
      update_dispatch_on_paris = paris.update_dispatch()
      response_body = response_handler(update_dispatch_on_paris, "Message: Dispatch was updated with new status")
    else:
      response_body = "Message: Resource is dispatch but event is not update or is not Paris group or status is pending. Not doing anything."
  
  else:
    response_body = "Message: Webhook resource is not 'route' or 'dispatch'. Not doing anything"

  response = {
          "statusCode": 200,
          "body": response_body
      }
  print({"Response Body": response_body})
  return response
