from utils.utils_create_content import create_dishes_by_category, create_dishes_by_category_subcategory_dishtype, create_dishes_by_subcategory
detailed_dishes = create_dishes_by_category_subcategory_dishtype(
    category="Italian", 
    number_of_subcategories=3, 
    number_of_dish_types=2, 
    number_of_dishes=3, 
    predefined_dish_types=["Appetizers", "Main Course", "Desserts"]
)

print(detailed_dishes)