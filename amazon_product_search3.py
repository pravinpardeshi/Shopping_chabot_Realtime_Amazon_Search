import requests

def query_amazon_direct(search_query):
    # 1. API Setup
    url = "https://real-time-amazon-data.p.rapidapi.com/search"

    # Replace with your RapidAPI Key
    headers = {
         "X-RAPIDAPI-Host": "real-time-amazon-data.p.rapidapi.com",
         "X-RapidAPI-Key": "5b9420d84cmshcf335c87c6f9fb0p12b17ejsnb0b95a220855",
    }

    # API specific parameters
    querystring = {
        "query": search_query,
        "page": "1",
        "country": "CA",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL"
    }

    try:
        print(f"Connecting to Amazon Real-Time Data for: '{search_query}'...")
        response = requests.get(url, headers=headers, params=querystring)

        # Check for 403 (Subscription) or 429 (Rate Limit) errors
        response.raise_for_status()

        res_data = response.json()

        # 2. Amazon-Specific Data Path
        # This API usually returns results inside data['products']
        products = res_data.get("data", {}).get("products", [])

        if not products:
            print("No Amazon products found. Check your subscription or query.")
            return []
        else:
            print("--- AVAILABLE KEYS FOR A PRODUCT ---")
            # Take the first product and list all its dictionary keys
            for key in products[0].keys():
                print(f"Key found: {key}")


        # 3. Parsing the Amazon Schema
        extracted_data = []
        for item in products:
            # Amazon API uses 'product_price' and 'product_title'
            product_info = {
                "asin": item.get("asin"),
                "title": item.get("product_title", "N/A"),
                "price": item.get("product_price", "N/A"),
                "rating": item.get("product_star_rating", "No rating"),
                "reviews": item.get("product_num_ratings", 0),
                "url": item.get("product_url"),
                "image": item.get("product_photo"),
                "is_prime": item.get("is_prime", False)
            }
            extracted_data.append(product_info)

        return extracted_data

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 403:
            print("❌ 403 Forbidden: You must subscribe to the plan on RapidAPI.")
        else:
            print(f"❌ HTTP Error: {err}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

# --- EXECUTION ---
if __name__ == "__main__":
    query = "Brooks Glycerin size 9.5 2E"
    amazon_results = query_amazon_direct(query)

    print(f"\nFound {len(amazon_results)} Amazon results:\n" + "="*50)

    # photo = item.get("product_photo", "") # This is the image URL

    for p in amazon_results[:10]: # Show top 10
        prime_tag = "[PRIME]" if p['is_prime'] else ""

        print(f"Id: {p['asin']}")
        print(f"Prime: {prime_tag}\nName: {p['title'][:65]}...")
        print(f"⭐ Rating: {p['rating']}\nReviews: ({p['reviews']} reviews) | 💰 {p['price']}")
        print(f"Image: {p['image']}")

        print(f"🔗 {p['url']}\n" + "-"*50)
















