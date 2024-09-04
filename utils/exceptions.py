from fastapi import HTTPException


def raise404_if_not(test_object, msg: str):
    if not test_object:
        raise HTTPException(status_code=404, detail=f'[not found] {msg}')
