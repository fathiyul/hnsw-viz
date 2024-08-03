const API_URL = 'http://localhost:8000/hsw';

async function makeRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

document.getElementById('generateArrays').addEventListener('click', async () => {
    const N = document.getElementById('arraySize').value;
    try {
        const result = await makeRequest('/generate_random_arrays', 'POST', { N: parseInt(N) });
        document.getElementById('results').innerHTML = `<p>${result.message}</p>`;
        if (result.visualization_path) {
            const timestamp = new Date().getTime();
            const imageUrl = `${API_URL}/visualizations/${result.visualization_path}?t=${timestamp}`;
            document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Data Visualization" style="max-width: 100%;">`;
        } else {
            document.getElementById('visualizations').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});

// document.getElementById('uploadArrays').addEventListener('click', async () => {
//     const fileInput = document.getElementById('arrayUpload');
//     const file = fileInput.files[0];
//     if (!file) {
//         alert('Please select a file first.');
//         return;
//     }
    
//     const formData = new FormData();
//     formData.append('file', file);
    
//     try {
//         const response = await fetch(`${API_URL}/upload_arrays`, {
//             method: 'POST',
//             body: formData
//         });
//         const result = await response.json();
//         document.getElementById('results').innerHTML = `<p>${result.message}</p>`;
//     } catch (error) {
//         document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
//     }
// });

document.getElementById('buildIndex').addEventListener('click', async () => {
    const k = document.getElementById('neighborCount').value;
    const distanceMetric = document.getElementById('distanceMetric').value;
    try {
        const result = await makeRequest('/build_index', 'POST', { k: parseInt(k), distance_metric: distanceMetric });
        document.getElementById('results').innerHTML = `<p>${result.message}</p>`;
        try {
            const timestamp = new Date().getTime();
            const response = await fetch(`${API_URL}/visualize_levels/?t=${timestamp}`);
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Levels Visualization" style="max-width: 100%;">`;
        } catch (error) {
            document.getElementById('visualizations').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});

document.getElementById('generateQueryVector').addEventListener('click', async () => {
    try {
        const result = await makeRequest('/generate_random_query_vector', 'POST');
        document.getElementById('results').innerHTML = `<p>Generated query vector: ${result.query_vector}</p>`;
        if (result.visualization_path) {
            const timestamp = new Date().getTime();
            const imageUrl = `${API_URL}/visualizations/${result.visualization_path}?t=${timestamp}`;
            document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Query Vector" style="max-width: 100%;">`;
        } else {
            document.getElementById('visualizations').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});

// document.getElementById('uploadQueryVector').addEventListener('click', async () => {
//     const fileInput = document.getElementById('queryVectorUpload');
//     const file = fileInput.files[0];
//     if (!file) {
//         alert('Please select a file first.');
//         return;
//     }
    
//     const formData = new FormData();
//     formData.append('file', file);
    
//     try {
//         const response = await fetch(`${API_URL}/upload_query_vector`, {
//             method: 'POST',
//             body: formData
//         });
//         const result = await response.json();
//         document.getElementById('results').innerHTML = `<p>Uploaded query vector: ${result.query_vector}</p>`;
//     } catch (error) {
//         document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
//     }
// });

document.getElementById('executeQuery').addEventListener('click', async () => {
    try {
        const result = await makeRequest('/query', 'POST', {});
        document.getElementById('results').innerHTML = `
            <p>Query Results:</p>
            <p>Nearest neighbor: ${result.nearest_neighbor}</p>
            <p>Distance: ${result.distance}</p>
        `;
        if (result.visualization_path) {
            const timestamp = new Date().getTime();
            const imageUrl = `${API_URL}/visualizations/${result.visualization_path}?t=${timestamp}`;
            document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Query Visualization" style="max-width: 100%;">`;
        } else {
            document.getElementById('visualizations').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
        document.getElementById('visualizations').innerHTML = '';
    }
});

document.getElementById('visualizeGraph').addEventListener('click', async () => {
    const level = document.getElementById('graphLevel').value;
    try {
        const timestamp = new Date().getTime();
        const response = await fetch(`${API_URL}/visualize_graph/${level}?t=${timestamp}`);
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('results').innerHTML = `<p>Graph visualization level-${level}</p>`;
        document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Graph Visualization" style="max-width: 100%;">`;
    } catch (error) {
        document.getElementById('visualizations').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});

document.getElementById('visualizeLevels').addEventListener('click', async () => {
    try {
        const timestamp = new Date().getTime();
        const response = await fetch(`${API_URL}/visualize_levels/?t=${timestamp}`);
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('results').innerHTML = `<p>Graph visualization: all levels</p>`;
        document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Levels Visualization" style="max-width: 100%;">`;
    } catch (error) {
        document.getElementById('visualizations').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});

document.getElementById('visualizeHistory').addEventListener('click', async () => {
    console.log('visualize history');
    try {
        const timestamp = new Date().getTime();
        const response = await fetch(`${API_URL}/visualizations/hnsw-query-history.png?t=${timestamp}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log(response);
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('visualizations').innerHTML = `<img src="${imageUrl}" alt="Query History Visualization" style="max-width: 100%;">`;
    } catch (error) {
        document.getElementById('visualizations').innerHTML = `<p>Error: ${error.message}</p>`;
    }
});