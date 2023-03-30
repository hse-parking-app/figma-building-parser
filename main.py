import sys
import json
import requests as re


def sent_to_url(parsed_json, url="http://localhost:8080"):
    with open(parsed_json, encoding="utf-8") as f:
        data = json.load(f)

    auth = {"Authorization": "Basic YWRtaW46YWRtaW4="}  # admin:admin

    post_building = {"name": data["name"], "address": data["address"], "numberOfLevels": data["numberOfLevels"]}
    response = re.post(url + "/building", json=post_building, headers=auth)
    building_id = response.json()["id"]
    print(f"{response.json()}")

    for level in list(data["levels"]):
        post_level = {"buildingId": building_id, "layerName": level["layerName"],
                      "numberOfSpots": level["numberOfSpots"],
                      "canvas": {"width": level["canvas"]["width"], "height": level["canvas"]["height"]}}
        response = re.post(url + "/parkingLevels", json=post_level, headers=auth)
        level_id = response.json()["id"]
        print(f"{response.json()}")
        for spot in list(level["spots"]):
            post_spot = {"isAvailable": spot["isAvailable"],
                         "isFree": True,
                         "canvas": {"width": spot["canvas"]["width"], "height": spot["canvas"]["height"]},
                         "onCanvasCoords": {"x": spot["onCanvasCoords"]["x"], "y": spot["onCanvasCoords"]["y"]},
                         "parkingNumber": spot["parkingNumber"],
                         "levelId": level_id,
                         "buildingId": building_id}
            response = re.post(url + "/parkingSpots", json=post_spot, headers=auth)
            print(f"{response.json()}")


def main(input_file="building.json", output_file="output.json"):
    f = open(input_file)
    data = json.load(f)

    levels = list(data["children"])
    levels.reverse()

    result = {"name": None,
              "address": None,
              "numberOfLevels": 0,
              "levels": []}
    for i in levels:
        if i["type"] == "FRAME":
            spots = list(i["children"])
            level = {"layerName": i["name"],
                     "numberOfSpots": len(spots),
                     "canvas": {"width": i["width"], "height": i["height"]},
                     "spots": []}
            for j in spots:
                spot = {"parkingNumber": None,
                        "isAvailable": None,
                        "isFree": True,
                        "canvas": {"width": j["width"], "height": j["height"]},
                        "onCanvasCoords": {"x": j["x"], "y": j["y"]}}
                spot_objs = list(j["children"])
                for k in spot_objs:
                    if k["type"] == "TEXT":
                        spot["parkingNumber"] = k["characters"]
                        if "fills" in k:
                            spot["isAvailable"] = True
                        else:
                            spot["isAvailable"] = False
                level["spots"].append(spot)
            result["levels"].append(level)
            result["numberOfLevels"] += 1
        else:
            if i["name"] == "Building name":
                result["name"] = i["characters"]
            if i["name"] == "Building address":
                result["address"] = i["characters"]

    with open(output_file, "w") as out:
        json.dump(result, out, indent=4, ensure_ascii=False)

    while True:
        print("Are you ready to send output.json to backend? y/n")
        inp = input().lower()
        if inp == "y":
            sent_to_url(output_file)
            break
        elif inp == "n":
            exit(0)
        else:
            continue


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
