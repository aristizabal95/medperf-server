from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
import yaml
import os
import aiofiles
from pydantic import BaseModel
from typing import Dict

app = FastAPI()


class Result(BaseModel):
    benchmark_uid: str
    model_uid: str
    dataset_uid: str
    scores: Dict[str, Dict[str, float]]


@app.get("/benchmarks/{uid}")
async def get_benchmark(uid):
    benchmark_path = os.path.join("app/database/benchmarks", uid + ".yaml")
    if not os.path.isfile(benchmark_path):
        raise HTTPException(status_code=404, detail="Benchmark not found")

    with open(benchmark_path, "r") as f:
        benchmark = yaml.full_load(f)

    return benchmark


@app.get("/cubes/{uid}", response_class=FileResponse)
async def get_cube(uid):
    cube_path = get_cube_path(uid)
    cube_file = os.path.join(cube_path, "mlcube.yaml")
    return cube_file


@app.get("/cubes/{uid}/metadata")
async def get_cube_metadata(uid):
    cube_path = get_cube_path(uid)
    metadata_file = os.path.join(cube_path, "metadata.yaml")
    with open(metadata_file, "r") as f:
        metadata = yaml.full_load(f)

    return metadata


@app.get("/cubes/{uid}/parameters-file", response_class=FileResponse)
async def get_cube_parameters(uid):
    cube_path = get_cube_path(uid)
    parameters_file = os.path.join(cube_path, "parameters.yaml")
    return parameters_file


@app.get("/cubes/{uid}/additional-files", response_class=FileResponse)
async def get_cube_parameters(uid):
    cube_path = get_cube_path(uid)
    parameters_file = os.path.join(cube_path, "additional_files.tar.gz")
    return parameters_file


def get_cube_path(uid):
    cube_path = os.path.join("app/database/cubes", uid)
    if not os.path.isdir(cube_path):
        raise HTTPException(status_code=404, detail="Cube not found")
    return cube_path


@app.post("/datasets")
async def upload_dataset(file: UploadFile = File(...)):
    write_path = os.path.join("app/database/datasets", file.filename)
    async with aiofiles.open(write_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    return {"Result": "OK"}


@app.post("/results")
async def upload_result(result: Result):
    bench = result.benchmark_uid
    model = result.model_uid
    dset = result.dataset_uid
    scores = result.scores
    write_path = os.path.join("app/database/results", bench, model, dset)
    if not os.path.isdir(write_path):
        os.makedirs(write_path)
    write_path = os.path.join(write_path, "results.yaml")
    with open(write_path, 'w') as f:
        yaml.dump(scores, f)
    return {"Result": "OK"}
