// this is the server

use std::io::{ ErrorKind, Write, Read};
use std::net::TcpListener;
use std::sync::mpsc;
use std::time::Duration;
use std::thread;

const LOCAL: &str = "127.0.0.1:3000";
// const LOCAL: &str = "112.134.184.8:3000";
const MSG_SIZE: usize = 32;

fn sleep() {
    thread::sleep( Duration::from_millis( 100 ) );
}

fn main() {
    let server = TcpListener::bind(LOCAL).expect("Listener failed to bind");
    server.set_nonblocking(true).expect("fail to init non-blocking");

    let mut clients = vec![];
    let (tx, rx) = mpsc::channel::<String>();
    println!(" start looking for clients " );
    loop {
        if let Ok( (mut socket, addr) ) = server.accept() {
            print!("one Client connected: {}" , addr );

            let tx = tx.clone();
            clients.push( socket.try_clone().expect("fail to clone client") );

            thread::spawn( move || loop {

                let mut buff = vec![0; MSG_SIZE ];

                match socket.read_exact( &mut buff ) {
                    Ok(_) => {
                        let msg = buff.into_iter().take_while( |&x| x != 0 ).collect::<Vec<_>>();
                        let msg = String::from_utf8( msg).expect("Invalid utf8 message");

                        print!("{}: {:?}", addr, msg);
                        tx.send(msg).expect("fail to send msg to rx");
                    }, 
                    Err( ref err) if err.kind() == ErrorKind::WouldBlock =>(), 
                    Err(_) => {
                        print!("Closing connection with: {}", addr);
                        break;
                    }

                }

                sleep();

            });
        }

        if let Ok( msg ) = rx.try_recv() {
            clients = clients.into_iter().filter_map( |mut client| {
                let mut buff = msg.clone().into_bytes();
                buff.resize(MSG_SIZE , 0);
                
                client.write_all( &buff).map( |_| client).ok()
                
            }).collect::<Vec<_>>();

        }
        
        sleep();
    }


}
