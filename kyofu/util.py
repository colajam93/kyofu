def compile_query(query) -> str:
    from kyofu import engine

    return query.statement.compile(engine, compile_kwargs={"literal_binds": True})


def show_proceed_prompt(message: str) -> bool:
    try:
        ok = input(f'{message} [y/N] ').strip().lower()
        return ok == 'y'
    except EOFError:
        pass
    return False
