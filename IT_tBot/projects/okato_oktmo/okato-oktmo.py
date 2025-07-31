import configparser
import requests
import json
import pandas as pd
import xlsxwriter  # Явный импорт xlsxwriter (нужен pandas)


def json_from_url_to_dataframes(
    url, max_depth=0, parent_data_list=None, depth=0, all_dfs=None
):
    """
    Загружает JSON данные из URL, рекурсивно обрабатывает дочерние элементы и возвращает словарь DataFrames.

    Args:
        url (str): URL для загрузки JSON данных.
        max_depth (int): Максимальная глубина рекурсии.
        parent_data_list (list, optional): Список словарей с данными родительских элементов. Defaults to None.
        depth (int, optional): Текущая глубина рекурсии. Defaults to 0.
        all_dfs (dict, optional): Словарь для хранения DataFrame для каждой глубины. Defaults to None.

    Returns:
        dict: Словарь, где ключ - глубина, значение - DataFrame.
    """

    if all_dfs is None:
        all_dfs = {}

    if depth > max_depth:
        print(
            f"Предупреждение: Достигнута максимальная глубина рекурсии ({max_depth})."
        )
        return all_dfs

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке данных из URL: {e}")
        return all_dfs
    except json.JSONDecodeError:
        print(f"Ошибка: Ответ от URL не является корректным JSON.")
        return all_dfs

    data_obj = data.get("data", {})
    feature_collection_properties = data_obj.get("properties", {})
    features = data_obj.get("features", [])

    if isinstance(feature_collection_properties, dict):
        feature_collection_header = list(feature_collection_properties.keys())
        prefixed_feature_collection_header = [
            "feature_collection_" + key for key in feature_collection_header
        ]
    else:
        print("Используется пустой заголовок для feature_collection_properties.")
        feature_collection_header = []
        prefixed_feature_collection_header = []

    if not features:
        print("Предупреждение: В JSON файле нет данных о 'features'.")
        return all_dfs

    first_feature = features[0] if features else None
    if not first_feature:
        print("Нет данных в features для определения заголовков.")
        return all_dfs

    properties = first_feature.get("properties", {})
    if isinstance(properties, dict):
        feature_header = list(properties.keys())
    else:
        print("Используется пустой заголовок для feature properties.")
        feature_header = []

    header = []
    parent_depth = 0
    if parent_data_list:
        for parent_data in parent_data_list:
            parent_header = [f"{key}_{parent_depth}" for key in parent_data.keys()]
            header.extend(parent_header)
            parent_depth += 1

    header.extend(
        [f"{key}_{parent_depth}" for key in prefixed_feature_collection_header]
    )
    header.extend([f"{key}_{parent_depth}" for key in feature_header])

    rows = []
    for feature in features:
        feature_properties = feature.get("properties", {})
        if not isinstance(feature_properties, dict):
            feature_properties = {}

        feature_collection_values = [
            feature_collection_properties.get(h, "") for h in feature_collection_header
        ]
        feature_values = [feature_properties.get(h, "") for h in feature_header]

        row = []
        if parent_data_list:
            for parent_data in parent_data_list:
                parent_values = [parent_data.get(key, "") for key in parent_data.keys()]
                row.extend(parent_values)

        row.extend(feature_collection_values)
        row.extend(feature_values)
        rows.append(row)

    df = pd.DataFrame(rows, columns=header)

    # Store DataFrame for current depth
    if depth not in all_dfs:
        all_dfs[depth] = df
    else:
        all_dfs[depth] = pd.concat([all_dfs[depth], df], ignore_index=True)

    # РЕКУРСИВНАЯ ОБРАБОТКА ДОЧЕРНИХ ЭЛЕМЕНТОВ
    for feature in features:  # Iterate through all features, not just the first
        feature_properties = feature.get("properties", {})
        if feature_properties.get("hasChildren") == True:
            oktmo = feature_properties.get("oktmo")
            if oktmo:
                child_url = url.split("&query=")[0] + f"&query={oktmo}"
                print(
                    f"Обнаружен дочерний элемент.  Рекурсивная загрузка с URL: {child_url} (глубина: {depth+1})"
                )

                current_data = {}
                for h in feature_collection_header:
                    current_data["feature_collection_" + h] = (
                        feature_collection_properties.get(h, "")
                    )
                for h in feature_header:
                    current_data[h] = feature_properties.get(h, "")

                new_parent_data_list = (
                    parent_data_list if parent_data_list else []
                ) + [current_data]

                all_dfs = json_from_url_to_dataframes(
                    child_url,
                    max_depth,
                    parent_data_list=new_parent_data_list,
                    depth=depth + 1,
                    all_dfs=all_dfs,  # Pass all_dfs dictionary
                )

    return all_dfs


def main():
    config = configparser.ConfigParser()
    config.read("./projects/okato_oktmo/config.ini")

    url = config["map"]["url"]
    max_depth = int(config["map"]["max_depth"])
    output_excel_file = config["map"]["output_excel_file"]

    all_dataframes = json_from_url_to_dataframes(url, max_depth=max_depth)

    if all_dataframes:
        try:
            with pd.ExcelWriter(output_excel_file, engine="xlsxwriter") as writer:
                for depth, df in all_dataframes.items():
                    df.to_excel(
                        writer, sheet_name=f"okato-oktmo-depth-{depth}", index=False
                    )
                print(
                    f"Данные успешно сохранены в {output_excel_file} с отдельными листами для каждой глубины."
                )
            return output_excel_file

        except Exception as e:
            print(f"Произошла ошибка при записи в Excel файл: {e}")
    else:
        print("Нет данных для записи в Excel файл.")


if __name__ == "__main__":
    main()
