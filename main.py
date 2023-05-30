import sys
import json
import requests as re


def sent_to_url(parsed_json, url):
    with open(parsed_json, encoding="utf-8") as f:
        data = json.load(f)

    response = re.post(url + "/auth/login", json={"email": "a@a.a", "password": "a"})

    auth = {"Authorization": "Bearer " + response.json()["accessToken"]}

    post_building = {"name": data["name"], "address": data["address"], "numberOfLevels": data["numberOfLevels"]}
    response = re.post(url + "/building", json=post_building, headers=auth)
    building_id = response.json()["id"]
    print(f"Took {response.elapsed.microseconds / 1000} ms {response.json()}")

    for level in list(data["levels"]):
        post_level = {"buildingId": building_id, "levelNumber": level["levelNumber"],
                      "numberOfSpots": level["numberOfSpots"],
                      "canvas": {"width": level["canvas"]["width"], "height": level["canvas"]["height"]}}
        response = re.post(url + "/parkingLevels", json=post_level, headers=auth)
        level_id = response.json()["id"]
        print(f"Took {response.elapsed.microseconds / 1000} ms {response.json()}")
        for spot in list(level["spots"]):
            post_spot = {"isAvailable": spot["isAvailable"],
                         "isFree": True,
                         "canvas": {"width": spot["canvas"]["width"], "height": spot["canvas"]["height"]},
                         "onCanvasCoords": {"x": spot["onCanvasCoords"]["x"], "y": spot["onCanvasCoords"]["y"]},
                         "parkingNumber": spot["parkingNumber"],
                         "levelId": level_id,
                         "buildingId": building_id}
            response = re.post(url + "/parkingSpots", json=post_spot, headers=auth)
            print(f"Took {response.elapsed.microseconds / 1000} ms {response.json()}")


def main(input_file="building.json", output_file="output.json", url="http://localhost:8080"):
    with open(input_file) as in_file:
        data = json.load(in_file)

    levels = list(data["children"])
    levels.reverse()

    result = {"name": None,
              "address": None,
              "numberOfLevels": 0,
              "levels": []}
    for i in levels:
        if i["type"] == "FRAME":
            spots = list(i["children"])
            level = {"levelNumber": int(i["name"]),
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

    with open(output_file, "w") as out_file:
        json.dump(result, out_file, indent=4, ensure_ascii=False)

    while True:
        print(f"Are you ready to send {output_file} to {url}? y/n")
        inp = input().lower()
        if inp == "y":
            sent_to_url(output_file, url)
            break
        elif inp == "n":
            exit(0)
        else:
            continue


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main()
