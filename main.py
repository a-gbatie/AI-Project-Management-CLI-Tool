"""Entry point for the project management CLI."""

from cli.commands import build_parser, ProjectCLI


def main():
  """Parse commands and run the application."""
  parser = build_parser()
  args = parser.parse_args()

  try:
    app = ProjectCLI()
    result = app.handle_command(args)

    if result:
      print(result)

  except (ValueError, RuntimeError) as error:
    parser.exit(
      status=1,
      message=f"Error: {error}\n"
    )


if __name__ == "__main__":
  main()