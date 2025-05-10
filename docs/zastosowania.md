# Zastosowania Devopy

## Nowe podejście do generowania i uruchamiania kodu

Devopy wprowadza rewolucyjne podejście do generowania i uruchamiania kodu. Zamiast tradycyjnego generowania statycznego kodu przez modele LLM, który następnie wymaga ręcznej integracji, Devopy odwraca tę koncepcję - **to nie kod jest generowany w LLM, ale dynamicznie uruchamiany jako usługa** według struktury narzuconej przez projekt.

## Dlaczego dekoratory?

Dekoratory w Pythonie stanowią idealny mechanizm do wzbogacania istniejącego kodu o nowe funkcjonalności bez naruszania jego struktury. W kontekście Devopy, dekoratory pozwalają na:

1. **Zachowanie czystej struktury projektu** - kod bazowy pozostaje niezmieniony
2. **Dodawanie złożonej funkcjonalności w sposób deklaratywny** - wystarczy dodać dekorator
3. **Separację logiki biznesowej od infrastruktury** - kod aplikacji skupia się na logice, dekorator zajmuje się infrastrukturą
4. **Łatwą konfigurację i parametryzację** - parametry dekoratora pozwalają dostosować zachowanie

## Przykłady zastosowań

### 1. Dynamiczne środowiska deweloperskie

Dekorator `editor_sandbox` automatycznie tworzy izolowane środowisko Docker dla aplikacji edytora:

```python
# Dekorator editor_sandbox wymaga funkcji, która:
# - Może przyjąć parametr 'sandbox' (obiekt EditorDockerSandbox)
# - Zwraca obiekt aplikacji (np. Flask app)
# - Opcjonalnie konfiguruje endpointy do interakcji z piaskownicą

@editor_sandbox(
    base_image="python:3.12-slim",  # Bazowy obraz Docker
    packages=["flask", "requests", "pandas"],  # Pakiety do zainstalowania w kontenerze
    ports={5000: 5000},  # Mapowanie portów (host:kontener)
    volumes={"/local/data": "/app/data"}  # Mapowanie woluminów (host:kontener)
)
def create_editor_app(sandbox=None):
    """
    Tworzy aplikację edytora kodu z piaskownicą Docker.
    
    Funkcja ta:
    1. Inicjalizuje aplikację Flask
    2. Konfiguruje endpointy do interakcji z piaskownicą Docker
    3. Umożliwia wykonywanie kodu w izolowanym środowisku
    
    Args:
        sandbox: Obiekt EditorDockerSandbox wstrzykiwany przez dekorator
        
    Returns:
        Aplikacja Flask gotowa do uruchomienia
    """
    app = Flask(__name__)
    
    @app.route('/execute-code', methods=['POST'])
    def execute_code():
        """Endpoint do wykonywania kodu Python w piaskownicy Docker"""
        code = request.json.get('code')
        # Wykonanie kodu w izolowanym środowisku
        result = sandbox.execute(["python", "-c", code])
        return jsonify(result)
    
    @app.route('/sandbox-status')
    def sandbox_status():
        """Endpoint do sprawdzania statusu piaskownicy Docker"""
        return jsonify({
            'ready': sandbox.ready,
            'container_id': sandbox.container_id,
            'image': sandbox.base_image
        })
    
    return app
```

### 2. Dynamiczne API generowane na podstawie danych

```python
# Dekorator api_generator wymaga funkcji, która:
# - Przyjmuje parametr 'api_context' (obiekt APIContext)
# - Może dostosować generowane API
# - Zwraca skonfigurowane API gotowe do uruchomienia

@api_generator(
    data_source="/path/to/database",  # Źródło danych (ścieżka, URL, connection string)
    api_type="graphql",  # Typ generowanego API (graphql, rest, grpc)
    authentication="jwt",  # Metoda uwierzytelniania
    rate_limit=100  # Limit zapytań na minutę
)
def create_data_api(api_context):
    """
    Tworzy dynamiczne API na podstawie struktury danych.
    
    Funkcja ta:
    1. Analizuje strukturę danych ze źródła
    2. Generuje odpowiednie endpointy/resolwery
    3. Konfiguruje uwierzytelnianie i autoryzację
    4. Dostosowuje zachowanie API do specyficznych wymagań
    
    Args:
        api_context: Obiekt APIContext wstrzykiwany przez dekorator,
                    zawierający wygenerowane API i metody do jego modyfikacji
        
    Returns:
        Skonfigurowane API gotowe do uruchomienia
    """
    # API jest automatycznie generowane na podstawie schematu danych
    # i udostępniane jako usługa
    
    # Można dostosować zachowanie API
    api_context.add_middleware(RateLimiter(max_requests=100))
    
    # Dodanie niestandardowego resolvera dla typu User
    @api_context.resolver('User')
    def custom_user_resolver(user_id):
        """Niestandardowy resolver dla typu User"""
        # Logika pobierania danych użytkownika
        return fetch_user_with_extended_data(user_id)
    
    # Dodanie niestandardowego endpointu
    @api_context.endpoint('/export-data')
    def export_data():
        """Endpoint do eksportu danych w różnych formatach"""
        format = request.args.get('format', 'json')
        return generate_export(format)
    
    return api_context.api
```

### 3. Automatyzacja procesów ETL

```python
# Dekorator data_pipeline wymaga funkcji, która:
# - Przyjmuje parametr 'pipeline' (obiekt DataPipeline)
# - Może przyjmować dodatkowe parametry (np. date)
# - Konfiguruje i uruchamia pipeline
# - Zwraca wynik przetwarzania

@data_pipeline(
    sources=[  # Źródła danych
        "postgres://user:pass@db1:5432/source_db", 
        "mongodb://user:pass@db2:27017/analytics"
    ],
    transformations=[  # Domyślne transformacje
        "normalize", 
        "deduplicate"
    ],
    destination="s3://data-warehouse/processed",  # Miejsce docelowe
    schedule="0 0 * * *"  # Harmonogram wykonania (cron)
)
def process_daily_data(pipeline, date=None):
    """
    Przetwarza dane z różnych źródeł i zapisuje wyniki w hurtowni danych.
    
    Funkcja ta:
    1. Pobiera dane z określonych źródeł
    2. Stosuje serię transformacji
    3. Zapisuje przetworzone dane w miejscu docelowym
    4. Generuje raport z przetwarzania
    
    Args:
        pipeline: Obiekt DataPipeline wstrzykiwany przez dekorator
        date: Data przetwarzania (domyślnie dzisiejsza)
        
    Returns:
        Podsumowanie wykonanego przetwarzania
    """
    # Ustawienie daty przetwarzania
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Konfiguracja pipeline'u
    pipeline.set_filter(f"date = '{date}'")
    
    # Dodanie niestandardowej transformacji
    @pipeline.transformation('business_logic')
    def custom_business_logic(data):
        """Niestandardowa transformacja danych biznesowych"""
        # Zastosowanie reguł biznesowych do danych
        data['revenue_category'] = data.apply(categorize_revenue, axis=1)
        data['customer_segment'] = data.apply(segment_customer, axis=1)
        return data
    
    # Dodanie powiadomień
    pipeline.on_success(send_success_notification)
    pipeline.on_failure(send_alert_notification)
    
    # Uruchomienie pipeline'u
    result = pipeline.run()
    
    # Generowanie i zapisywanie raportu
    report = generate_processing_report(result)
    save_report(report, f"reports/{date}_etl_report.pdf")
    
    return result.summary
```

### 4. Mikrousługi generowane na żądanie

```python
# Dekorator microservice_generator wymaga funkcji, która:
# - Przyjmuje parametr 'spec' (obiekt ServiceSpec)
# - Konfiguruje specyfikację usługi
# - Zwraca skonfigurowaną usługę gotową do uruchomienia

@microservice_generator(
    service_type="user-management",  # Typ usługi
    database="postgres",  # Baza danych
    cache="redis",  # System cache
    auth="oauth2",  # System uwierzytelniania
    deployment={  # Konfiguracja wdrożenia
        "replicas": 3,
        "resources": {
            "cpu": "0.5",
            "memory": "512Mi"
        }
    }
)
def user_service(spec):
    """
    Tworzy mikrousługę zarządzania użytkownikami.
    
    Funkcja ta:
    1. Konfiguruje endpointy usługi
    2. Definiuje modele danych
    3. Konfiguruje połączenia z bazą danych i cache
    4. Dostosowuje zachowanie usługi
    
    Args:
        spec: Obiekt ServiceSpec wstrzykiwany przez dekorator,
             zawierający wygenerowaną specyfikację usługi
        
    Returns:
        Skonfigurowana usługa gotowa do uruchomienia
    """
    # Mikrousługa jest generowana na podstawie specyfikacji
    # i uruchamiana jako kontener Docker
    
    # Definiowanie modeli danych
    spec.define_model('User', {
        'id': 'uuid',
        'username': 'string',
        'email': 'string',
        'created_at': 'timestamp'
    })
    
    # Dodanie niestandardowego endpointu
    @spec.endpoint('/users/export', methods=['GET'], auth_required=True)
    def export_users_handler():
        """Endpoint do eksportu danych użytkowników"""
        format = request.args.get('format', 'json')
        users = spec.db.query('SELECT * FROM users')
        return export_data(users, format)
    
    # Konfiguracja limitów zapytań
    spec.set_rate_limit('/users', 200)
    spec.set_rate_limit('/users/{id}', 500)
    
    # Dodanie middleware
    spec.add_middleware(LoggingMiddleware())
    spec.add_middleware(ErrorHandlingMiddleware())
    
    # Konfiguracja cache
    spec.cache_config({
        'user_profile': {'ttl': 300},  # 5 minut
        'user_permissions': {'ttl': 600}  # 10 minut
    })
    
    return spec.service
```

### 5. Automatyczne testowanie w izolowanych środowiskach

```python
# Dekorator test_environment wymaga funkcji, która:
# - Przyjmuje parametr 'test_env' (obiekt TestEnvironment)
# - Konfiguruje i uruchamia testy
# - Zwraca wyniki testów

@test_environment(
    fixtures=["users.json", "products.json"],  # Dane testowe
    mocks=["payment_gateway", "email_service"],  # Usługi do zmockowania
    coverage=True,  # Włączenie pomiaru pokrycia kodu
    parallel=4  # Liczba równoległych procesów testowych
)
def run_integration_tests(test_env):
    """
    Uruchamia testy integracyjne w izolowanym środowisku.
    
    Funkcja ta:
    1. Konfiguruje środowisko testowe
    2. Ładuje dane testowe
    3. Uruchamia testy
    4. Generuje raporty z wyników
    
    Args:
        test_env: Obiekt TestEnvironment wstrzykiwany przez dekorator
        
    Returns:
        Wyniki testów
    """
    # Środowisko testowe jest automatycznie konfigurowane
    # z załadowanymi fixtures i zmockowanymi usługami
    
    # Konfiguracja niestandardowych mocków
    @test_env.mock('payment_gateway')
    def mock_payment_process(amount, card_details):
        """Mock dla bramki płatności"""
        return {
            'transaction_id': f'test-{uuid.uuid4()}',
            'status': 'success',
            'amount': amount
        }
    
    # Dodanie niestandardowych fixtures
    test_env.add_fixture('special_products.json')
    
    # Konfiguracja zmiennych środowiskowych dla testów
    test_env.set_env({
        'TEST_MODE': 'true',
        'API_TIMEOUT': '5000'
    })
    
    # Uruchomienie testów w izolowanym środowisku
    results = test_env.run_tests('tests/integration/')
    
    # Generowanie raportów
    test_env.generate_report('coverage.html')
    test_env.generate_report('test_results.xml', format='junit')
    
    # Analiza wyników
    if results.failed_count > 0:
        print(f"UWAGA: {results.failed_count} testów nie powiodło się!")
        for test in results.failed_tests:
            print(f"- {test.name}: {test.error}")
    
    return results
```

## Zastosowanie w różnych domenach

### Analiza danych i uczenie maszynowe

- Automatyczne tworzenie środowisk do eksperymentów ML
- Dynamiczne generowanie pipeline'ów przetwarzania danych
- Izolowane środowiska do trenowania modeli

### Rozwój aplikacji webowych

- Automatyczne konfigurowanie środowisk deweloperskich
- Dynamiczne generowanie API na podstawie modeli danych
- Izolowane środowiska do testowania funkcjonalności

### DevOps i infrastruktura

- Automatyczne tworzenie i zarządzanie kontenerami
- Dynamiczne konfigurowanie środowisk CI/CD
- Izolowane środowiska do testowania infrastruktury

### Edukacja i prototypowanie

- Bezpieczne środowiska do nauki programowania
- Szybkie prototypowanie rozwiązań
- Izolowane środowiska do eksperymentów

## Korzyści z podejścia opartego na dekoratorach

1. **Łatwość użycia** - wystarczy dodać dekorator do istniejącej funkcji
2. **Modularność** - każdy dekorator odpowiada za konkretny aspekt funkcjonalności
3. **Separacja odpowiedzialności** - kod aplikacji skupia się na logice biznesowej, dekoratory zajmują się infrastrukturą
4. **Elastyczność** - parametry dekoratorów pozwalają na dostosowanie zachowania
5. **Bezpieczeństwo** - izolowane środowiska Docker zwiększają bezpieczeństwo wykonywania kodu

## Wnioski z doświadczeń

Nasze doświadczenia z rozwojem Devopy pokazują, że podejście oparte na dekoratorach jest szczególnie wartościowe w kontekstach, gdzie:

1. **Trudno o jedno uniwersalne rozwiązanie** - dekoratory pozwalają dostosować zachowanie do konkretnych przypadków
2. **Potrzebna jest dynamiczna adaptacja do danych** - usługi mogą być generowane i konfigurowane na podstawie struktury danych
3. **Izolacja jest kluczowa** - każda usługa działa w swoim własnym środowisku
4. **Struktura projektu powinna pozostać czysta** - dekoratory nie wymagają zmian w istniejącym kodzie

Najnowsze rozwiązanie z dekoratorem `editor_sandbox` jest przykładem tego podejścia - pozwala nie tylko generować kod, ale także automatycznie tworzyć i zarządzać całym środowiskiem wykonawczym, co znacząco upraszcza proces rozwoju i wdrażania.
