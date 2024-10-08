import streamlit as st
import tensorflow as tf

# Define your model structure
Dense = tf.keras.layers.Dense
Attn = tf.keras.layers.MultiHeadAttention
Dropout = tf.keras.layers.Dropout

L2Norm = tf.keras.layers.Lambda(lambda x: tf.math.l2_normalize(x, axis=1), name='L2norm')

class sampling(tf.keras.layers.Layer):
    def call(self, inputs):
        mean, log_var = inputs
        z = tf.random.normal(shape=tf.shape(mean))
        return mean + z * tf.exp(0.5 * log_var)

def build(N):
    inp = tf.keras.Input((N, 2))
    x = inp
    x = Dense(32, activation='relu')(x)
    x0 = x
    x, _ = Attn(1, 128, name='attention0')(x, x, return_attention_scores=True)
    x = tf.keras.layers.Concatenate()([x0, x])
    x = tf.keras.layers.Flatten()(x)
    x = Dense(128, activation='relu')(x)
    x = [Dense(64, activation='relu')(x) for _ in range(2)]
    x = sampling()(x)
    x = L2Norm(x)
    h = x

    x = Dense(128, activation='relu')(h)
    x = Dropout(0.5)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.5)(x)
    outR = Dense(N, activation=None, name='outR')(x)

    x = Dense(128, activation='relu')(h)
    x = Dropout(0.5)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.5)(x)
    out1 = Dense(1, activation='sigmoid', name='out1')(x)

    x = Dense(128, activation='relu')(h)
    x = Dropout(0.5)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.5)(x)
    out2 = Dense(3, activation='softmax', name='out2')(x)

    x = tf.keras.Model(inp, (outR, out1, out2))
    x.compile(optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-5),
              loss={'outR': tf.keras.losses.MeanSquaredError(),
                    'out1': tf.keras.losses.BinaryFocalCrossentropy(),
                    'out2': tf.keras.losses.CategoricalCrossentropy()},
              metrics={'outR': ['mae', 'mse'],
                       'out1': [tf.keras.metrics.AUC(name='auc1', curve='PR')],
                       'out2': [tf.keras.metrics.AUC(name='auc2', curve='PR')]})
    return x

# Load the model
model = build(5)
fold = 'full'
model.load_weights(f'k{fold}_best.weights.h5')

# Streamlit app title and description
st.title("Neuroblastoma Prediction")
st.write("Upload Plasma and Urine Metabolites")

# File uploader
uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

if uploaded_file is not None:
    # Read the uploaded file
    document = uploaded_file.read().decode()

    # Preprocess the document to extract data for the model
    # Assuming the document contains a structured format that you can parse
    # For demonstration, we're using dummy data. Replace this with actual data extraction.
    # For example: data = parse_document(document)
    data = tf.random.normal((1, 5, 2))  # Replace this with actual parsed data

    # Predict using the model
    predictions = model.predict(data)

    # Display predictions
    st.write("Predictions:")
    st.write("Status of Disease:", predictions[1])
    st.write("Local of Tumor:", predictions[2])
    #st.write("Categorical Classification Output:", predictions[2])
