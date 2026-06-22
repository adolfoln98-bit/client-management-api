from fastapi import HTTPException, Depends
from security import(
    get_usuario_actual,
    get_admin_user
)


def requerir_admin(usuario_actual = Depends(get_usuario_actual)):
    try:
        print(usuario_actual)
        return get_admin_user(usuario_actual)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))