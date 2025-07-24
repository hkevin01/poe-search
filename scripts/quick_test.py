import poe

# Use your decoded cookies directly
p_b = "AG58MLIXFnbOh98QAv4YHA=="

try:
    client = poe.Client(p_b)
    print("✅ Client created successfully!")
    
    # Test a simple message
    response = client.send_message("Assistant", "Hello! Just testing the connection.")
    print("✅ Message sent successfully!")
    print("Response:", response)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("This might be normal - some unofficial APIs have rate limits or restrictions")