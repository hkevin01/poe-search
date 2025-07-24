import browser_cookie3
import json

def get_poe_cookies():
    try:
        # Try Chrome first
        cookies = browser_cookie3.chrome(domain_name='poe.com')
        poe_cookies = {}
        
        for cookie in cookies:
            if cookie.name in ['p-b', 'p-lat']:
                poe_cookies[cookie.name] = cookie.value
        
        return poe_cookies
    except:
        # Try Firefox if Chrome fails
        try:
            cookies = browser_cookie3.firefox(domain_name='poe.com')
            poe_cookies = {}
            
            for cookie in cookies:
                if cookie.name in ['p-b', 'p-lat']:
                    poe_cookies[cookie.name] = cookie.value
                    
            return poe_cookies
        except Exception as e:
            print(f"Could not extract cookies: {e}")
            return None

if __name__ == "__main__":
    cookies = get_poe_cookies()
    if cookies:
        print("Found cookies:", cookies)
        # Save to file
        with open('.env', 'w') as f:
            for key, value in cookies.items():
                f.write(f"POE_{key.upper().replace('-', '_')}={value}\n")
        print("Cookies saved to .env file")
    else:
        print("No cookies found. Make sure you're logged into poe.com in your browser.")