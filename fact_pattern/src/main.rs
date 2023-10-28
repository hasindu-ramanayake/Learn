mod game;
mod magic_maze;
mod normal_maze;

use magic_maze::MagicMaze;
use normal_maze::NormalMaze;

fn main( ) {
    let normal_maze_1 = NormalMaze::new();
    game::run(normal_maze_1);

    let magic_maze_1 = MagicMaze::new();
    game::run(magic_maze_1);

}