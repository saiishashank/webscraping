import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import plotly.express as px

current_date = datetime.now()
fdate=current_date.strftime("%d-%b-%Y")
productslist=[]
def send_request():
    baseurl='https://www.noon.com'
    try:
        for i in range(1,5):
            ##requesting using proxys that are provided by scrapingbee.com
            response = requests.get(
                url='https://app.scrapingbee.com/api/v1',
                params={
                    'api_key': '64QXSRTBOB5GZFXCM4656Y0JFBIZ8EDPIRAT72QWDQ8JK0LMG1NW29HGFMW27JT1WPXW17UGF70590KP',
                    'url': f"https://www.noon.com/uae-en/sports-and-outdoors/exercise-and-fitness/yoga-16328/?isCarouselView=false&limit=50&page={i}&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc"
                },
            )
            print('Response HTTP Status Code:', response.status_code)

            # Check for successful response
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all product divs
                products = soup.find_all('div', class_='eSrvHE')
                if not products:
                    print("No products found.")
                    return
                
                # Extract and print links from the products
                
                for product in products:
                    product_link = product.find('a')
                    purl=baseurl + product_link['href']
                    pname_div=product.find('div',class_='dOJDLL')
                    pname=pname_div['title']
                    brand=pname_div.find('span').find('span')
                    if not brand:
                        brand="NA"
                    else:
                        brand=brand.text.split(' ')[0]
                    avg_rating=product.find('div',class_='dGLdNc')
                    if not avg_rating:
                        avg_rating=0
                    else:
                        avg_rating=float(avg_rating.text)
                    rating_count=product.find('span',class_='DkxLK')
                    if not rating_count:
                        rating_count=0
                    else:
                        rating_count=rating_count.text
                        if 'K' in rating_count:
                            rating_count=int(float(rating_count.replace('K',''))*1000)
                        else:
                            rating_count=int(rating_count)
                        
                    express=product.find('div',class_='dFzhiL')
                    if not express:
                        express="NA"
                    else:
                        img=express.find('img')
                        if img:
                            exptype=img['alt']
                            if exptype!="noon-express":
                                express="N"
                            else:
                                express="Y"
                    sp=product.find('strong',class_='amount')
                    if not sp:
                        sp=0
                    else:
                        sp=float(sp.text.replace(',', ''))
                    oldp=product.find('span',class_='oldPrice')
                    if not oldp:
                        oldp=0
                    else:
                        oldp=float(oldp.text.replace(',', ''))
                    product_id=purl.split('/')[5]
                    sponsored=product.find('div',class_='gzboVs')
                    if not sponsored:
                        sponsored="N"
                    else:
                        sponsored="Y"
                    
                    productslist.append({
                        "Date": fdate,
                        "SKU":product_id,
                        "Name": pname,
                        "Brand": brand,
                        "Average Rating": avg_rating,
                        "Rating Count": rating_count,
                        "sponsored":sponsored,
                        "price":oldp,
                        "Sales Price": sp,
                        "Express":express,
                        "Link": purl,
                        
                    })
                    print("product name:",pname)                    
            else:
                print("Failed to fetch content. Server returned status code:", response.status_code)
    
    except requests.RequestException as e:
        print("An error occurred while making the request:", e)

send_request()
df=pd.DataFrame(productslist)
df.to_csv('noon.csv')
def visualize_data(df):
    # Top 5 Most Expensive Products
    most_expensive = df.nlargest(5, 'Sales Price')
    fig1 = px.bar(
        most_expensive,
        x='Sales Price',
        y='Name',
        color='Sales Price',
        orientation='h',
        title='Top 5 Most Expensive Products',
        labels={'Sales Price': 'Price', 'Name': 'Product Name'},
    )
    fig1.update_layout(title_font_size=14, xaxis_title_font_size=12, yaxis_title_font_size=12)
    fig1.show()

    #  Top 5 Cheapest Products
    cheapest = df.nsmallest(5, 'Sales Price')
    fig2 = px.bar(
        cheapest,
        x='Sales Price',
        y='Name',
        color='Sales Price',
        orientation='h',
        title='Top 5 Cheapest Products',
        labels={'Sales Price': 'Price', 'Name': 'Product Name'},
    )
    fig2.update_layout(title_font_size=14, xaxis_title_font_size=12, yaxis_title_font_size=12)
    fig2.show()

    #  Number of Products by Brand
    brand_counts = df['Brand'].value_counts().reset_index()
    brand_counts.columns = ['Brand', 'Number of Products']
    fig3 = px.bar(
        brand_counts,
        x='Number of Products',
        y='Brand',
        color='Number of Products',
        orientation='h',
        title='Number of Products by Brand',
        labels={'Number of Products': 'Count', 'Brand': 'Brand'},
    )
    fig3.update_layout(title_font_size=14, xaxis_title_font_size=12, yaxis_title_font_size=12)
    fig3.show()

visualize_data(df)
