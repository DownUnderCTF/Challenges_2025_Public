#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
from Crypto.Cipher import AES
import base64
import secrets
import os

app = FastAPI()

KEY = secrets.token_bytes(16)
SECRET = os.getenv("SECRET").encode()


class Plaintext(BaseModel):
    data: str  # base64-encoded plaintext


class BatchRequest(BaseModel):
    data: list[str]  # list of base64-encoded plaintexts


def pad(msg: bytes) -> bytes:
    pad_len = 16 - len(msg) % 16
    return msg + b" " * pad_len


def aes_ecb_encrypt_b64(b64_input: str) -> str:
    try:
        pt = base64.b64decode(b64_input)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid base64 input")

    full_pt = pt + SECRET
    pt_padded = pad(full_pt)
    cipher = AES.new(KEY, AES.MODE_ECB)
    ct = cipher.encrypt(pt_padded)
    return base64.b64encode(ct).decode()


@app.post("/encrypt")
async def encrypt_single(req: Plaintext):
    return {"ciphertext": aes_ecb_encrypt_b64(req.data)}


@app.post("/encrypt_batch")
async def encrypt_batch(req: BatchRequest):
    if len(req.data) > 256:
        raise HTTPException(status_code=400, detail="batch too large (max 256)")
    return {"ciphertexts": [aes_ecb_encrypt_b64(s) for s in req.data]}


app.mount("", StaticFiles(directory="./dist/", html=True), name="frontend")
