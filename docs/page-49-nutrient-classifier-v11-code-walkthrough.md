# Page 49 — Nutrient Classifier V11: Code Walkthrough

Line-by-line explanation of the top-level constants in `scripts/nutrient_classifier_v11.py`.

---

```python
BATCH_SIZE = 32
```

Number of training samples processed per gradient update during model training. TensorFlow feeds 32 image+sensor pairs through the network at a time, computes the loss, and updates the weights — then repeats for the next batch. Smaller batches use less GPU memory but produce noisier gradients; 32 is a common default that balances the two.

---

```python
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M')
```

Captures the current date and time at the moment the script runs, formatted as e.g. `20260612_1430`. Used on the next line to name the output model file:

```python
MODEL_SAVE_PATH = f'leafcloud_multimodal_v11_{TIMESTAMP}.keras'
```

Each training run saves to a uniquely named file like `leafcloud_multimodal_v11_20260612_1430.keras`, preventing previous runs from being overwritten.

---

```python
SENSOR_NORM = {
    'ph':         (3.0, 10.0),
    'ec':         (0.0, 1.6),
    'water_temp': (24.0, 29.0),
}
```

Defines the min/max range for each sensor reading, used to normalize raw values to a 0–1 scale before feeding them into the model.

For example, a pH of 6.5 becomes `(6.5 - 3.0) / (10.0 - 3.0) ≈ 0.5`. This ensures all three sensor inputs are on the same scale so no single feature dominates training due to its unit magnitude.

---

```python
LABEL_LIST = ['Water', 'NPK', 'Micro', 'Mix']
```

Defines the four nutrient treatment classes the model classifies leaf images into:

- **Water** — plain water, no nutrients
- **NPK** — macro nutrients (Nitrogen, Phosphorus, Potassium)
- **Micro** — micronutrients
- **Mix** — combination of the above

---

```python
LABEL_TO_IDX = {l: i for i, l in enumerate(LABEL_LIST)}
```

A **dict comprehension** that converts `LABEL_LIST` into a label-to-integer mapping.

- `enumerate(LABEL_LIST)` produces pairs: `(0, 'Water'), (1, 'NPK'), (2, 'Micro'), (3, 'Mix')`
- `for i, l in ...` unpacks each pair into index `i` and label `l`
- `l: i` makes the label the key and the index the value

Result: `{'Water': 0, 'NPK': 1, 'Micro': 2, 'Mix': 3}` — used during training to convert string labels into integers the model can process.

---

```python
engine = create_engine(DB_URL)
```

Creates a SQLAlchemy database connection engine — the entry point for all database operations in the script. It does not open a connection immediately; it sets up the configuration so that when `fetch_raw_data(engine)` is called, SQLAlchemy knows how and where to connect (PostgreSQL host, port, credentials, database name) to run the SQL queries that pull training data.

---

```python
df = pd.read_sql(query, engine)
```

Executes the SQL query against the database and loads the results directly into a Pandas DataFrame. Each row in `df` becomes one training sample — containing the image file path, the three sensor readings (pH, EC, water temp), and the bucket label (Water/NPK/Micro/Mix). The rest of the script then uses this DataFrame to load images, normalize sensor values, and feed everything into model training.
