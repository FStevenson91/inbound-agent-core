from real_estate_agent.tools.crm import create_contact

# Probar la función directamente
result = create_contact(
    name="Test User",
    email="test@test.com", 
    phone_number="123456789"
)

print("Resultado:", result)