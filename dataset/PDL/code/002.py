import requests

def can_item_be_shipped(country, item):
    if not country or not item:
        return "Please provide both the target country and the item information."

    # Call the 'Check If Item Can Be Shipped' API
    shipping_status_response = requests.get('https://api.example.com/query_shipping_status', params={'country': country, 'goods': item})
    
    if shipping_status_response.status_code == 200:
        shipping_status_data = shipping_status_response.json()
        
        if shipping_status_data['isValid']:
            return f"The item '{item}' can be shipped to {country}. Please note that this information is for reference only and the final decision is based on the destination customs clearance requirements."
        else:
            # Call the 'Get Item List' API to get the list of supported item categories for that country
            item_list_response = requests.get('https://api.example.com/query_goods_list', params={'country': country})
            
            if item_list_response.status_code == 200:
                item_list_data = item_list_response.json()
                supported_items = ', '.join(item_list_data['goods_list'])
                return f"The item '{item}' cannot be shipped to {country}. Supported item categories for {country} are: {supported_items}. Please note that this information is for reference only and the final decision is based on the destination customs clearance requirements."
            else:
                return "Failed to retrieve the list of supported item categories. Please contact local DHL for further assistance."
    else:
        return "Query failed. Destination shipping restriction information was not found. Please contact local DHL for further assistance."

# Example usage:
country = "Germany"
item = "Electronics"
print(can_item_be_shipped(country, item))