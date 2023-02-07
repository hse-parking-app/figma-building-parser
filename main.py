import json
import requests as re


def sendTo(url: str):
    f = open("output.json")
    data = json.load(f)

    auth = {"Authorization": "Basic YWRtaW46YWRtaW4="}  # admin:admin

    postBuilding = {"name": data["name"], "address": data["address"], "numberOfLevels": data["numberOfLevels"]}
    response = re.post(url + "/building", json=postBuilding, headers=auth)
    buildingId = response.json()["id"]
    print(f"{response.json()}")

    for level in list(data["levels"]):
        postLevel = {"buildingId": buildingId, "layerName": level["layerName"],
                     "numberOfSpots": level["numberOfSpots"],
                     "canvas": {"width": level["canvas"]["width"], "height": level["canvas"]["height"]}}
        response = re.post(url + "/parkingLevels", json=postLevel, headers=auth)
        levelId = response.json()["id"]
        print(f"{response.json()}")
        for spot in list(level["spots"]):
            postSpot = {"isFree": True,
                        "canvas": {"width": spot["canvas"]["width"], "height": spot["canvas"]["height"]},
                        "onCanvasCoords": {"x": spot["onCanvasCoords"]["x"], "y": spot["onCanvasCoords"]["y"]},
                        "parkingNumber": spot["parkingNumber"], "levelId": levelId, "buildingId": buildingId}
            response = re.post(url + "/parkingSpots", json=postSpot, headers=auth)
            print(f"{response.json()}")


def main():
    f = open("building.json")
    data = json.load(f)

    result = {"name": data["name"], "address": "demo_address"}

    levels = list(data["children"])
    levels.reverse()
    result["numberOfLevels"] = len(levels)
    result["levels"] = []
    for i in levels:
        level = {"layerName": i["name"]}
        spots = list(i["children"])
        level["numberOfSpots"] = len(spots)
        level["canvas"] = {"width": i["width"], "height": i["height"]}
        level["spots"] = []
        for j in spots:
            spot = {"isFree": True}
            rectext = list(j["children"])
            for k in rectext:
                if k["type"] == "RECTANGLE":
                    spot["canvas"] = {"width": k["width"], "height": k["height"]}
                    spot["onCanvasCoords"] = {"x": round(k["x"]), "y": round(k["y"])}
                else:
                    spot["parkingNumber"] = k["name"]
            level["spots"].append(spot)
        result["levels"].append(level)

    with open("output.json", "w") as out:
        print(json.dumps(result, indent=4), file=out)

    while True:
        print("Are you ready to send output.json to backend? y/n")
        inp = input().lower()
        if inp == "y":
            sendTo("http://localhost:8080")
            break
        elif inp == "n":
            exit(0)
        else:
            continue


if __name__ == '__main__':
    main()
