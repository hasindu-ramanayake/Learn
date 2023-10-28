use super::game::{ MazeGame, Room};

#[derive(Clone)]
pub struct NormalRoom {
    room_id: u32,
}

impl NormalRoom {
    pub fn new( room_id: u32 ) ->Self {
        Self { room_id}
    }
}

impl Room for NormalRoom {
    fn render( &self ) {
        println!("Normal Room #{}", self.room_id);
    }
}

pub struct NormalMaze{
    rooms: Vec<NormalRoom>,
}

impl NormalMaze {
    pub fn new() ->Self {
        Self {
            rooms: vec![ NormalRoom::new(1), NormalRoom::new(2)]
        }
    }
}

impl MazeGame for NormalMaze {
    type RoomImpl = NormalRoom;

    fn rooms(&self )-> Vec<Self::RoomImpl> {
        let mut rooms = self.rooms.clone();
        rooms.reverse();
        rooms
    }

}