import pandas as pd
import time
import ollama
import ast

def get_response(prompt: str):
    response = ollama.chat(model='gemma2:27b', messages=[{'role': 'user', 'content': prompt}])
    input_text = response['message']['content']
    
    # Find the start and end of the array in the response
    start_index = input_text.find('[')
    end_index = input_text.find(']') + 1
    
    # Extract the array as a string and use literal_eval to convert to a list
    array_str = input_text[start_index:end_index]
    
    # Safely evaluate the string to a Python list
    try:
        array = ast.literal_eval(array_str)
    except (SyntaxError, ValueError):
        # Handle cases where the string is not a valid Python list
        return []
    
    return array

def get_answer(prompt: str):
    response = ollama.chat(model='gemma2:27b', messages=[{'role': 'user', 'content': prompt}])
    answer = response['message']['content']
    return answer

def create_dishes_by_category(category, number_of_dishes, already_created_dishes):
    """
    LEVEL 1: Generates dishes for a single category.
    
    Parameters:
        category (str): The type of dishes to generate (e.g., 'Italian', 'Desserts', 'Vegan').
        number_of_dishes (int): The number of new dish names to generate.
        already_created_dishes (list): A list of previously created dish names.
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Category', 'Dish_Name', and 'Description'.
    """
    start_time = time.time()
    data = []
    
    # Fetch dish names based on the category and required number
    dishes = get_response(f'create {number_of_dishes} authentic dish names (not recipes) in the category of {category} cuisine. Give dish names in array form [......,....]')
    
    # Append each generated dish name into the data list
    for dish in dishes:
        data.append({
            'Category': category,
            'Dish_Name': dish
        })
    
    # Append each already created dish to the data list
    for dish in already_created_dishes:
        data.append({
            'Category': category,
            'Dish_Name': dish
        })
    
    # For each dish in the data list, get an entertaining description
    for item in data:
        dish_text = item['Dish_Name']
        print(dish_text)
        # Fetch an entertaining description
        description = get_answer(f'Give a short and entertaining description for the dish: {dish_text} from {category} cuisine. Focus on what makes it special and delicious.')
        print(description)
        item['Description'] = description
    
    # Convert list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    end_time = time.time()
    print(f"Runtime: {end_time - start_time} seconds")
    
    return df


def create_dishes_by_subcategory(category, number_of_subcategories, number_of_dishes, already_created_dishes):
    """
    LEVEL 2: Generates dishes organized by category and subcategory.
    
    Parameters:
        category (str): The main cuisine or food tradition (e.g., 'Italian', 'Asian', 'Mediterranean').
        number_of_subcategories (int): The number of subcategories to generate within the main category.
        number_of_dishes (int): The number of new dish names to generate per subcategory.
        already_created_dishes (list): A list of pre-existing dish names to add to each subcategory.
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Category', 'Subcategory', 'Dish_Name', and 'Description'.
    """
    # Initialize a list to store dish data
    start_time = time.time()
    data = []
    
    # Fetch the list of subcategories (regional cuisines or cooking styles within the main cuisine)
    subcategories = get_response(
        f'give me a list of {number_of_subcategories} subcategories or regions within {category} cuisine. Present the results in a python array like [..., ...]'
    )
    
    # Check that subcategories is returned as a list
    if not isinstance(subcategories, list):
        raise ValueError("Expected 'subcategories' to be a list.")
    
    # Loop over each subcategory to generate and collect dish names
    for subcategory in subcategories:
        # Fetch new dish names for the current subcategory
        dishes = get_response(
            f'give me {number_of_dishes} authentic dish names from {subcategory} {category} cuisine. Provide only the dish names in array form like [..., ...]. Do not include descriptions.'
        )
        print(dishes)
        
        # Ensure dishes is a list
        if not isinstance(dishes, list):
            raise ValueError("Expected 'dishes' to be a list.")
        
        # Append each generated dish name with its category and subcategory to the data list
        for dish in dishes:
            data.append({
                'Category': category,
                'Subcategory': subcategory,
                'Dish_Name': dish
            })
        
        # Add the same set of predefined dishes for the current subcategory
        for dish in already_created_dishes:
            data.append({
                'Category': category,
                'Subcategory': subcategory,
                'Dish_Name': dish
            })
    
    # For each dish in the data list, get a description
    for item in data:
        dish_name = item['Dish_Name']
        # Fetch the description in an entertaining way
        description = get_answer(f'describe the dish {dish_name} from {item["Subcategory"]} {category} cuisine in a short, entertaining way. Focus only on the description.')
        print(description)
        # Add the description to a new key 'Description'
        item['Description'] = description
    
    # Convert list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    end_time = time.time()
    print(f"Runtime: {end_time - start_time} seconds")
    
    return df


def create_dishes_by_category_subcategory_dishtype(category, number_of_subcategories, number_of_dish_types, number_of_dishes, predefined_dish_types):
    """
    LEVEL 3: Generates dishes organized by category, subcategory, and dish type.
    
    Parameters:
        category (str): The main cuisine or food tradition (e.g., 'Italian', 'Asian', 'Mediterranean').
        number_of_subcategories (int): The number of subcategories to generate within the main category.
        number_of_dish_types (int or None): The number of dish types to generate within each subcategory.
                                           If None, skip dish type generation and only use predefined types.
        number_of_dishes (int): The number of new dish names to generate per dish type.
        predefined_dish_types (list): A list of pre-existing dish types to add to each subcategory
                                     (e.g., ['Appetizers', 'Main Course', 'Desserts']).
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Category', 'Subcategory', 'Dish_Type', 'Dish_Name', and 'Description'.
    """
    # Initialize a list to store dish data
    start_time = time.time()
    data = []
    
    # Fetch the list of subcategories (regional cuisines or cooking styles within the main cuisine)
    subcategories = get_response(
        f'give me a list of {number_of_subcategories} subcategories or regions within {category} cuisine. Present the results in a python array like [..., ...]'
    )
    print(subcategories)
    
    # Check that subcategories is returned as a list
    if not isinstance(subcategories, list):
        raise ValueError("Expected 'subcategories' to be a list.")
    
    # Loop over each subcategory to generate and collect dish names
    for subcategory in subcategories:
        # Check if dish type generation is enabled
        if number_of_dish_types is not None:
            # Fetch the list of dish types for each subcategory
            dish_types = get_response(
                f'give me a list of {number_of_dish_types} specific dish types or categories within {subcategory} {category} cuisine. Each should be a concise category name (e.g., Pasta, Soups, Grilled Meats), not full dishes. Present the list in a python array format, like [..., ...]'
            )
            
            # Check that dish_types is returned as a list
            if not isinstance(dish_types, list):
                raise ValueError("Expected 'dish_types' to be a list.")
            
            # Combine dynamically generated and predefined dish types
            all_dish_types = dish_types + predefined_dish_types
        else:
            # Only use predefined dish types if dish type generation is skipped
            all_dish_types = predefined_dish_types
        
        print(all_dish_types)
        
        # Loop over each dish type to generate dish names
        for dish_type in all_dish_types:
            # Fetch new dish names for the current dish type
            dishes = get_response(
                f'give me {number_of_dishes} authentic dish names (not recipes) for {dish_type} in {subcategory} {category} cuisine. Provide only the dish names in array form like [..., ...]. Do not include descriptions.'
            )
            
            # Ensure dishes is a list
            if not isinstance(dishes, list):
                raise ValueError("Expected 'dishes' to be a list.")
            
            # Append each generated dish name with its category, subcategory, and dish type to the data list
            for dish in dishes:
                data.append({
                    'Category': category,
                    'Subcategory': subcategory,
                    'Dish_Type': dish_type,
                    'Dish_Name': dish
                })
    
    # For each dish in the data list, get a description
    for item in data:
        dish_name = item['Dish_Name']
        # Fetch the description in an entertaining way
        description = get_answer(f'describe the dish {dish_name}, a {item["Dish_Type"]} from {item["Subcategory"]} {category} cuisine, in a short, entertaining way. Focus only on the description.')
        print(description)
        # Add the description to a new key 'Description'
        item['Description'] = description
    
    # Convert list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    end_time = time.time()
    print(f"Runtime: {end_time - start_time} seconds")
    
    return df