from real_estate_agent.tools.crm import get_contact, create_contact

# Test 1: Buscar contacto que no existe
result = get_contact("123456789")
print("GET (no existe):", result)

# Test 2: Crear contacto
result = create_contact(name="Test User", phone="123456789", email="test@test.com")
print("CREATE:", result)

# Test 3: Buscar contacto que ahora existe
result = get_contact("123456789")
print("GET (existe):", result)