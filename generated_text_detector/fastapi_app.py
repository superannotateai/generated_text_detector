import argparse
import logging
import json
import os

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from generated_text_detector.controllers.detect import router as detect_router
from generated_text_detector.controllers.ping import router as health_router
from generated_text_detector.utils.aggregated_detector import AggregatedDetector

with open("./version.txt") as f:
    version = f.read()

app = FastAPI(
    title="Generated Text Detector",
    description="Service for detection generated text and return score that text was generated",
    version=version,
    root_path="/generated-text-detector",
)

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect_router)
app.include_router(health_router)


def parse_args():
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = "8080"
    DEFAULT_DETECTOR_CONFIG_PATH = "etc/configs/detector_config.json"
    DEFAULT_DEVICE = "cuda:0"
    
    parser = argparse.ArgumentParser(
        description="SuperAnnotate service for Generated Text Detection"
    )
    parser.add_argument(
        "--host",
        help=f"Host of service (default: {DEFAULT_HOST})",
        default=DEFAULT_HOST,
        type=str,
    )
    parser.add_argument(
        "--port",
        "-p",
        help=f"Port of service (default: {DEFAULT_PORT})",
        default=DEFAULT_PORT,
        type=int,
    )
    parser.add_argument(
        "--detector-config-path",
        "-dc",
        help=f"Path to a detector config file (defult: {DEFAULT_DETECTOR_CONFIG_PATH})",
        default=DEFAULT_DETECTOR_CONFIG_PATH,
        type=check_path,
    )
    parser.add_argument(
        "--device",
        "-d",
        help=f"Device for inference model.",
        default=DEFAULT_DEVICE,
        type=str,
    )
    return parser.parse_args()


def check_path(path: os.PathLike) -> os.PathLike|None:
    if not isinstance(path, os.PathLike):
        raise TypeError("The variable is not a string (path).")

    # Check if the path exists
    if not os.path.exists(path):
        raise TypeError(f"The path '{path}' does not exist.")

    return path


def create_app(
    path_to_detector_config: os.PathLike,
    device: str
):
    
    with open(path_to_detector_config, 'r') as f:
        detector_conf = json.load(f)

    application = app

    detector = AggregatedDetector(
        text_detector_model_name_or_path = detector_conf["text_detector_model"],
        code_default_score = detector_conf["code_default_probability"],
        device = device,
    )
    
    setattr(application, "detector", detector)

    class EndpointFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.getMessage().find(f"/segmentation/healthcheck") == -1

    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    return application


if __name__ == "__main__":
    import uvicorn

    args = parse_args()
    app = create_app(args.detector_config_path, args.device)
    uvicorn.run(app, host=args.host, port=args.port)
else:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    app = create_app(os.environ.get("DETECTOR_CONFIG_PATH"), device)
