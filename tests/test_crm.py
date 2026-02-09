from real_estate_agent.tools.crm import get_contact, create_contact

# Buscar contacto que no existe
result = get_contact("123456789")
print("GET (no existe):", result)

# Crear contacto
result = create_contact(name="Test User", phone="123456789", email="test@test.com")
print("CREATE:", result)

# Buscar contacto que ahora existe
result = get_contact("123456789")
print("GET (existe):", result)