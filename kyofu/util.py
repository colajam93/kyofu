def compile_query(query) -> str:
    from kyofu import engine

    return query.statement.compile(engine, compile_kwargs={"literal_binds": True})
