export async function initialize() {
    console.log("Started")
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
    console.log("Done")
    return data;
}

export async function getBlobInformation() {
    const response = await fetch("http://127.0.0.1:8000/blobs")
    const data = await response.json()
    return data
}

export async function getWorldMetrics(){
    const response = await fetch("http://127.0.0.1:8000/world_metrics")
    const data = await response.json()
    return data
}

export async function wait(){
  const response = await fetch("http://127.0.0.1:8000/run_iteration?temperature=0.7&create_image=false")
  const data = await response.json()
  return data
}

export async function proposePolicy(policy) {
  const response = await fetch('http://127.0.0.1:8000/propose_policy', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'accept': 'application/json'
    },
    body: JSON.stringify({
      "proposal": policy,
      "temperature": .7
    })
  });

  const data = await response.json();
  console.log("Done")
  return data;
}