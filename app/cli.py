import click
from . import image_generator as app

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.option("-n", "--name", type=str, help="Name to say hello to", default="Guest")
def hello(name):
    click.echo(f"Hello again {name}!")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "object_directories",
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    "-b",
    "--backgrounds",
    type=click.Path(exists=True),
    help="Folder location for images to be used as backgrounds",
)
@click.option(
    "-os",
    "--object_size",
    type=int,
    help="Size of the objects. Objects are rendered in square bounding boxes of given size",
    default=18,
)
@click.option(
    "-o",
    "--output_directory",
    type=click.Path(exists=False),
    help="Directory where generated images should be stored",
    default="scatter_yolo_images",
)
@click.option(
    "-min",
    "--min_objects",
    type=int,
    help="Minimum number of objects to scatter",
    default=50,
)
@click.option(
    "-max",
    "--max_objects",
    type=int,
    help="Maximum number of objects to scatter",
    default=100,
)
@click.option(
    "-c",
    "--image_count",
    type=int,
    help="Number of images to generate (default=1)",
    default=1,
)
@click.option(
    "-s",
    "--image_size",
    type=int,
    help="Size of image(s) to generate (default=500).",
    default=500,
)
@click.option(
    "-cx",
    "--cluster_idx",
    type=float,
    help="Index ranges from 0-1. A value of 1 implies maximum clustering",
    default=1.0,
)
@click.option(
    "-pad",
    "--image_padding",
    type=int,
    help="Number of pixels inside the image border where objects should not be placed",
    default=10,
)
@click.option(
    "-v",
    "--verbose",
    type=bool,
    help="Generate images noisily",
    default=False,
)
@click.option(
    "-anim",
    "--generate_animation",
    type=bool,
    help="Generate object placement animation gifs along with the images",
    default=False,
)
def generate(
    object_directories,
    backgrounds,
    object_size,
    min_objects,
    max_objects,
    image_count,
    image_size,
    output_directory,
    cluster_idx,
    image_padding,
    verbose,
    generate_animation,
):
    """
    Generate images with objects in OBJECT_DIRECTORIES scattered in them. Additionally generates YOLO annotations for each image.
    """
    if len(object_directories) == 0:
        print("No objects provided to scatter. Exiting..")
    else:
        click.echo("Generating images...")
        try:
            image_generator = app.SyntheticGenerator(
                object_directories,
                backgrounds_dir=backgrounds,
                object_size=object_size,
                image_size=image_size,
                image_padding=image_padding,
            )
            image_generator.generete(
                number_images=image_count,
                cluster_idx=cluster_idx,
                min_objects=min_objects,
                max_objects=max_objects,
                save_dir=output_directory,
                verbose=verbose,
                animate=generate_animation,
            )
        except:
            print("Something went wrong, and image generation was not completed.")
