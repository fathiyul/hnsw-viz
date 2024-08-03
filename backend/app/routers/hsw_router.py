from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import os
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.hsw_service import HSWService
from app.services.viz_service import plot_data
import numpy as np
import io

router = APIRouter()
hsw_service = None
generated_arrays = None
generated_query_vector = None
NDIM = 2

class BuildIndexParams(BaseModel):
    k: int
    distance_metric: str = "l2"

class QueryRequest(BaseModel):
    query_vector: Optional[List[float]] = None

class RandomArraysParams(BaseModel):
    N: int

@router.post("/generate_random_arrays")
async def generate_random_arrays(params: RandomArraysParams):
    global generated_arrays
    generated_arrays = np.random.rand(params.N, NDIM)
    visualization_path = plot_data(generated_arrays)
    return {
        "message": f"Generated {params.N} random arrays with {NDIM} dimensions",
        "visualization_path": visualization_path
    }


@router.post("/upload_arrays")
async def upload_arrays(file: UploadFile = File(...)):
    global generated_arrays, NDIM
    
    if not file.filename.endswith('.npy'):
        return JSONResponse(status_code=400, content={"message": "Only .npy files are allowed"})
    
    content = await file.read()
    npy_data = np.load(io.BytesIO(content))
    
    if len(npy_data.shape) != 2 or npy_data.shape[1] != NDIM:
        return JSONResponse(status_code=400, content={"message": f"Array should be of shape (N,{NDIM})"})
    
    generated_arrays = npy_data
    return JSONResponse(status_code=200, content={"message": f"Successfully uploaded array with shape {npy_data.shape}"})

@router.post("/build_index")
async def build_index(params: BuildIndexParams):
    global hsw_service, generated_arrays
    if generated_arrays is None:
        raise HTTPException(status_code=400, detail="No arrays generated. Please generate arrays first.")
    
    hsw_service = HSWService(len(generated_arrays), params.k, params.distance_metric)
    hsw_service.set_data(generated_arrays)
    hsw_service.build_index()
    return {"message": "Index built successfully"}

@router.get("/get_graph")
async def get_graph():
    if hsw_service is None:
        raise HTTPException(status_code=400, detail="Index not built yet")
    graph = hsw_service.get_graph()
    return {"graph": graph}

@router.get("/get_levels")
async def get_levels():
    if hsw_service is None:
        raise HTTPException(status_code=400, detail="Index not built yet")
    return hsw_service.get_levels()

@router.post("/generate_random_query_vector")
async def generate_random_query_vector():
    global generated_query_vector
    generated_query_vector = np.random.rand(NDIM).tolist()
    visualization_path = plot_data(generated_arrays, generated_query_vector)
    return {"query_vector": generated_query_vector, "visualization_path": visualization_path}

@router.post("/upload_query_vector")
async def upload_query_vector(file: UploadFile = File(...)):
    global generated_query_vector, NDIM
    
    if not file.filename.endswith('.npy'):
        return JSONResponse(status_code=400, content={"message": "Only .npy files are allowed"})
    
    content = await file.read()
    npy_data = np.load(io.BytesIO(content))
    
    if npy_data.shape != (NDIM,):
        return JSONResponse(status_code=400, content={"message": f"Query vector should be of shape ({NDIM},)"})
    
    generated_query_vector = npy_data.tolist()
    return JSONResponse(status_code=200, content={"message": "Successfully uploaded query vector", "query_vector": generated_query_vector})

@router.post("/query")
async def query(request: QueryRequest):
    try:
        query_vector = request.query_vector
        if query_vector is None:
            query_vector = generated_query_vector
        result_node, distance, visualization_path = hsw_service.query(query_vector)
        result = {"nearest_neighbor": result_node, "distance": distance, "visualization_path": visualization_path}
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/visualizations/{file_name}")
async def get_visualization(file_name: str):
    file_path = f"visualizations/{file_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Visualization not found")

@router.get("/visualize_graph/{level}")
async def visualize_graph(level: int):
    try:
        file_path = hsw_service.visualize_graph(level)
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/visualize_levels")
async def visualize_levels():
    try:
        file_path = hsw_service.visualize_levels()
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
