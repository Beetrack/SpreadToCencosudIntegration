import json, os
from pkg.paris_handler import ParisHandler
from pkg.spread_handler import SpreadHandler
from pkg.beetrack_api import BeetrackAPI
from pkg.commons import fetch_tag_value

def integrate(event, context):
  print(event)
  body = json.loads(event['body'])
  print(body)
  paris = ParisHandler(body)
  spread = SpreadHandler(body)
  account_id_spread = os.environ.get("account_id_spread")
  account_id_paris = os.environ.get("account_id_paris")
  print(account_id_spread, account_id_paris)
  print("Account ID :", body.get("account_id"))
  print(body.get("resource"),body.get("event"),body.get("account_id"))

  if (body.get("resource") == "route" and body.get("event") == "update" and body.get("account_id") == int(account_id_paris)):
    paris_route_id = body.get("route")
    print("Paris trunk route id :", paris_route_id)
    get_paris_route = BeetrackAPI(os.environ.get("paris_api_key")).get_route(paris_route_id)
    print("Paris route including dispatches :", get_paris_route)
    get_trunk_dispatches = spread.get_spread_trunk_dispatches(get_paris_route)
    print("Paris trunk route dispatches :", get_trunk_dispatches)

    if get_trunk_dispatches == []:
      print("Paris trunk route does not belong to Spread or doesn't have any Spread dispatch.")
      response_body = "Message: Trunk route does not belong to Spread or doesn't have any Spread dispatch."

    else:
      truck_identifier = "PAR-" + body.get("truck")
      print("Paris vehicle on Spread :", truck_identifier)
      verify_spread_truck = spread.check_or_create_trucks(truck_identifier)
      print("Verify existence Paris truck on Spread :", verify_spread_truck)
      create_trunk_route_on_spread = spread.create_new_trunk_route(verify_spread_truck, get_trunk_dispatches)
      print("Response after creating a Paris trunk route in Spread :", create_trunk_route_on_spread)
      response_body = "Message: Trunk route was created on Spread"

  elif (body.get("resource") == "dispatch" and body.get("event") == "update" and body.get("account_id") == int(account_id_spread) and body.get("is_trunk") == True):
      print({"Handler If Case" : "Update Trunk Dispatch"})
      update_trunk_dispatch_on_paris = paris.update_trunk_dispatch()
      print()
      response_body = "Message: Dispatch was updated with new status"

  elif (body.get("resource") == "route" and body.get("event") == "start" and body.get("account_id") == int(account_id_spread)):
    print({"Handler If Case" : "Start Route"})
    spread_route_id = body.get("route")
    route_start_at = body.get("started_at")
    spread_route = BeetrackAPI(os.environ.get("spread_group_api_key")).get_route(spread_route_id)
    print("Spread route (id : {}) started at {} :".format(spread_route_id, route_start_at), spread_route)

    if not spread_route:
      print("Route does not exist or doesn't have any Paris dispatch.")
      response_body = "Message: Route does not exist or doesnt have Paris dispatches"

    else:
      truck_identifier = "SPR-" + body.get("truck")
      print("Spread vehicle on Paris :", truck_identifier)
      verify_paris_truck = paris.check_or_create_trucks(truck_identifier)
      print("Verify existence Paris truck on Spread :", verify_paris_truck)
      get_paris_dispatches = paris.create_paris_dispatches(spread_route)
      print("Dispatches within Spread's route belonging to Paris :", get_paris_dispatches)
      create_route_on_paris = paris.create_new_route(verify_paris_truck, get_paris_dispatches)
      print("Response after creating Spread rute on Paris :", create_route_on_paris)
      new_paris_route_id = create_route_on_paris.get('response').get('route_id')
      start_paris_route = paris.start_route(new_paris_route_id, route_start_at)
      print("Response after starting Spread rute on Paris :", start_paris_route)
      response_body = "Message: Route was created and Started correctly"

  elif (body.get("resource") == "dispatch" and body.get("event") == "update" and body.get("account_id") == int(account_id_spread) and body.get("is_trunk") == False):
    print({"Handler If Case" : "Update Spraed dispatches on Paris"})
    group_name = fetch_tag_value(body.get("groups"), "name")
    if group_name == "PARIS" and body.get("status") != 1:
      update_dispatch_on_paris = paris.update_dispatch()
      print("Respnse for updating Spread dispatches on Paris :",update_dispatch_on_paris)
      response_body = "Message: Dispatch was updated with new status"
    else:
      response_body = "Message: Resource is dispatch but event is not update or is not Paris group or status is pending. Not doing anything."
  
  elif (body.get("resource") == "route" and body.get("event") == "finish" and body.get("account_id") == int(account_id_spread)):
    print({"Handler If Case" : "Finish Route"})
    ended_at = body.get("ended_at")
    route_id = body.get("route")
    finish_paris_route = paris.finish_route(ended_at, route_id, int(os.environ.get("tag_route")))
    print ({"Beetrack Response for Ending Route" : finish_paris_route})
    response_body = "Message: Route was Ended"

  else:
    response_body = "Message: Webhook resource is not 'route' or 'dispatch'. Not doing anything"

  response = {
          "statusCode": 200,
          "body": response_body
      }
  print({"Response Body": response_body})
  return response
