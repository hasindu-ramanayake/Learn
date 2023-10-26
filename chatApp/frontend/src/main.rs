use std::io::{self, ErrorKind, Read, Write};
use std::net::TcpStream;
use std::sync::mpsc::{self, TryRecvError};
use std::thread;
use std::time::Duration;

const LOCAL: &str = "127.0.0.1:3000";
// const LOCAL: &str = "112.134.184.8:3000";

const MSG_SIZE: usize = 32;



fn main() {

    println!("Start running main");
    let mut client = TcpStream::connect(LOCAL).expect("Stream file to connect");
    client.set_nonblocking(true).expect("file to init non-blocking");
    
    print!(" TcpString set");

    let (tx, rx) = mpsc::channel::<String>();

    thread::spawn( move || loop {

        let mut buff = vec![0; MSG_SIZE];
        match client.read_exact( &mut buff ) {
            Ok(_) => {
                let msg = buff.into_iter().take_while( |&x| x != 0 ).collect::<Vec<_>>();
                print!("message rec {:?}", msg);
            }, 
            Err( ref err) if err.kind() == ErrorKind::WouldBlock => (),
            Err(_) => {
                print!( "connection with server was off");
                break;
            }
        }

        match rx.try_recv() {
            Ok(msg) => {
                let mut buff = msg.clone().into_bytes();
                buff.resize(MSG_SIZE, 0);
                client.write_all(&buff).expect("Write to socket fail");
                print!("message send {:?}", msg);
            },
            Err ( TryRecvError::Empty ) => (),
            Err ( TryRecvError::Disconnected ) => break

        }

        
        thread::sleep( Duration::from_millis(100) );

    });


    print!("Write a message: ");

    loop {
        let mut buff = String::new();
        io::stdin().read_line(&mut buff).expect("reading rom stdin failed");
        let msg = buff.trim().to_string();
        if msg==":q" || tx.send(msg).is_err() {break}
    }
    print!("Closing connection");


}
