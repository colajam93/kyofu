def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('base_path')
    parser.add_argument('-d', '--output-path', required=False, default='.')
    return parser.parse_args()


def main() -> None:
    from pathlib import Path
    from mutagen import File
    import pickle

    args = parse_args()
    base_path = Path(args.base_path).resolve()
    output_base_path = Path(args.output_path).resolve()
    for p in base_path.rglob('*'):
        out_path = output_base_path / p.relative_to(base_path)
        if p.is_dir():
            print('process: path={}'.format(
                p.resolve()
            ))
            out_path.mkdir(parents=True, exist_ok=True)
        else:
            with p.open('rb') as f:
                guess = File(f, easy=True)
            if not guess:
                print('failed guess: path={}'.format(
                    p.resolve()
                ))
                continue
            filename = f'{p.name}.pickle'
            dumpfile = out_path.parent / filename
            with dumpfile.open('wb') as f:
                pickle.dump(guess, f)


if __name__ == '__main__':
    main()
