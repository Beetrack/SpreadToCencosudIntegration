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
  resource = body.get("resource")
  event = body.get("event")
  truck = body.get("truck")
  truck_dispatch = body.get("truck_identifier")
  is_trunk = body.get("is_trunk")
  is_pickup = body.get("is_pickup")
  paris_trucks = ["LCXK43", "SPRE01"]
  account_id = body.get("account_id")
  print({"Event from Account ID": account_id})

  if (resource == "route" and event == "update" and account_id == int(account_id_paris) and (truck in paris_trucks)):
    # Clone Paris trunk route on Spread account.
    print({"Handler if case": "Paris Trunk Route"})
    paris_route_id = body.get("route")
    print({" Paris Trunk Route": paris_route_id})
    get_paris_route = BeetrackAPI(os.environ.get("paris_api_key"), os.environ.get('paris_url')).get_route(paris_route_id) 
    print({" Get Route Info": get_paris_route})
    get_trunk_dispatches = spread.get_spread_trunk_dispatches(get_paris_route)
    if get_trunk_dispatches == []:
      print({ " Case":"Paris trunk route does not belong to Spread or doesn't have any Spread dispatches"})
      response = "Message: Trunk route does not belong to Spread or doesn't have any Spread dispatch."
    else:
      print({ " Case":"Creating trunk route in Spread"})
      truck_identifier = "PAR-" + body.get("truck")
      verify_spread_truck = spread.check_or_create_trucks(truck_identifier)
      create_trunk_route_on_spread = spread.create_new_trunk_route(verify_spread_truck, get_trunk_dispatches)
      if create_trunk_route_on_spread:
        response = {"statusCode": 200, "body": "Message: Trunk route was created in Spread."}
      else: 
        response = {"statusCode": 500, "body": "Message: Trunk route wasn't created in Spread."} 
  
  elif (resource == "dispatch" and event == "update" and account_id == int(account_id_paris) and is_trunk == True and body.get("status") == 1 and (truck_dispatch in paris_trucks)):
    # Get id dispatch of the dispatches of Paris and added to a tag associated to the Spread dispatches.
    print({"Handler If Case" : "Update Paris dispatch in Spread"})
    verify_dispatch_existance = spread.verify_existence_in_spread()
    response =  verify_dispatch_existance

  elif (resource == "dispatch" and event == "update" and account_id == int(account_id_spread) and is_trunk == True and body.get('status') != 1):
    # Update status in trunk dispatch on Paris account.
    print({"Handler If Case" : "Update Trunk Dispatch in Paris"})
    update_trunk_dispatch_on_paris = paris.update_trunk_dispatch()
    response = update_trunk_dispatch_on_paris

  elif (resource == "dispatch" and event== "update" and account_id == int(account_id_spread) and ((is_trunk == False and is_pickup == False) or (is_trunk == False and is_pickup == True))):
    # Update trunk dispatches with last mile status in Paris account
    print({"Handler If Case" : "Update LastMile dispatches in Paris"})
    group_name = fetch_tag(body.get("groups"), "name")
    print({"Dispatch Belongs To The Group" : group_name})
    if group_name == "Paris" and (body.get("status") in [1,2,3,4]):
      update_dispatch_on_paris = paris.update_dispatch()
      response = update_dispatch_on_paris  
    else:
      response = {"statusCode": 200, "body": "Message: Resource is dispatch but event is not update or is not Paris group or status is pending. Not doing anything."}
  
  elif resource == "test_redis":
    test_redis = spread.test_redis()
    print(test_redis)
    response = {"statusCode": 200, "body": "Message: Prueba redis"}

  else:
    response = {"statusCode": 200, "body": "Message: In case of a route webhook event isn't update or belong to LCXK43 or SPRE01 trucks. In case of a dispatch webhook don't belog to a Spread-Paris route."}

  print({"Response": response})
  return response
