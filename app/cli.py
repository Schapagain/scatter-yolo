import click
from . import image_generator as app
from datetime import datetime
import multiprocessing
import math
from os.path import join

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


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
    default=26,
    show_default=True,
)
@click.option(
    "-o",
    "--output_directory",
    type=click.Path(exists=False),
    help="Directory where generated images should be stored",
    default="scatter_yolo_images",
    show_default=True,
)
@click.option(
    "-min",
    "--min_objects",
    type=int,
    help="Minimum number of objects to scatter",
    default=50,
    show_default=True,
)
@click.option(
    "-max",
    "--max_objects",
    type=int,
    help="Maximum number of objects to scatter",
    default=100,
    show_default=True,
)
@click.option(
    "-c",
    "--image_count",
    type=int,
    help="Number of images to generate",
    default=1,
    show_default=True,
)
@click.option(
    "-s",
    "--image_size",
    type=int,
    help="Size of image(s) to generate.",
    default=500,
    show_default=True,
)
@click.option(
    "-cx",
    "--cluster_idx",
    type=float,
    help="Index ranges from 0-1. A value of 1 implies maximum clustering",
    default=0.2,
    show_default=True,
)
@click.option(
    "-pad",
    "--image_padding",
    type=int,
    help="Number of pixels inside the image border where objects should not be placed",
    default=10,
    show_default=True,
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
@click.option(
    "-sh",
    "--shape",
    type=str,
    help="Shape of the final image (rect or circ)",
    default="rect",
    show_default=True,
)
@click.option(
    "-rat",
    "--scatter-ratio",
    type=str,
    help="Relative proportions of objects",
    default=None,
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
    shape,
    scatter_ratio,
):
    """
    Generate images with objects in OBJECT_DIRECTORIES scattered in them. Additionally generates YOLO annotations for each image.
    """
    scatter_ratios = []
    if len(object_directories) == 0:
        print("No objects provided to scatter. Exiting..")
    else:

        try:
            if scatter_ratio:
                scatter_ratios = list(map(float, scatter_ratio.split(",")))
                print(scatter_ratios, scatter_ratio, object_directories)
                if len(scatter_ratios) != len(object_directories):
                    click.echo(
                        "Ratios length does not match the number of objects provided. Exiting.."
                    )
                    raise Exception()
            click.echo("Generating images...")
            image_generator = app.SyntheticGenerator(
                object_directories,
                backgrounds_dir=backgrounds,
                object_size=object_size,
                image_size=image_size,
                image_padding=image_padding,
            )
            
            processes = []
            start_time = datetime.now()
            MAX_IMAGES_PER_PROCESS = 10
            num_generated = 0
            num_process_required = math.ceil(image_count/MAX_IMAGES_PER_PROCESS)
            for process_num in range(num_process_required):
                process_image_count = min(image_count-process_num*MAX_IMAGES_PER_PROCESS,MAX_IMAGES_PER_PROCESS)
                p = multiprocessing.Process(target=image_generator.generete,kwargs=dict(
                number_images=process_image_count,
                cluster_idx=cluster_idx,
                min_objects=min_objects,
                max_objects=max_objects,
                save_dir=output_directory,
                verbose=verbose,
                file_name_prefix=str(process_num),
                animate=generate_animation,
                shape=shape,
                scatter_ratios=scatter_ratios,))
                processes.append(p)
                p.start()
                num_generated += process_image_count
            
            for p in processes:
                p.join()

            print(
                f"Generated {num_generated} images in {(datetime.now() - start_time).total_seconds():.3f} seconds."
            )
        except Exception as e:
            print("Something went wrong, and image generation was not completed.", e)
