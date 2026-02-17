from utils.file_management import load_yaml, save_yaml

func_path = "/home/surender/surender/celllabs/new_engineeros/app/phase_5/func_nonfunc.yaml"



def func_tech():
    data = load_yaml(func_path)

    optimized_data = [
        {"id": func["id"], "description": func["description"], "related_usecase": func["related_usecase"]}
        for func in data["functional_requirements"]
    ]

    return optimized_data



def non_tech():
    data = load_yaml(func_path)

    # print(type(data["non_functional_requirements"][0]["related_fr"]))


    optimized_data = [
        {"id": func["id"], "description": func["description"], "related": func["related_fr"]}
        for func in data["non_functional_requirements"]
        if "related_fr" in func
    ]

    # optimized_data = []
    # for i in data["non_functional_requirements"]:
    #     print(i["related_fr"])
    #     data = {"id": i["id"], "description": i["description"], "related": i["related_fr"]}
    #     optimized_data.append(i)

    return optimized_data


final_data = {
    "functional_requirements": func_tech(),
    "non_functional_requirements": non_tech()
}


out_path = "/home/surender/surender/celllabs/new_engineeros/app/phase_5/opt_func_nonfunc.yaml"
save_yaml(out_path, final_data)


# print(final_data)
