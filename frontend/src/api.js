export async function initialize() {
    const response = await fetch('http://127.0.0.1:8000/initialize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json'
      },
      body: JSON.stringify({
        "num_blobs": 8,
        "num_societies": 3
      })
    });

    const data = await response.json();
    return data;
}

export async function getBlobInformation() {
    const response = await fetch("http://127.0.0.1:8000/blobs")
    const data = await response.json()
    return data
}