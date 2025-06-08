import { useState } from 'react'

import Square from "./components/Square"
import './App.css'

export default function App() {
  const [turn, setTurn] = useState(0)
  const [value, setValue] = useState(Array.from({length: 3},()=> Array.from({length: 3}, () => " ")));
  var labelheader = "Welcome to tic-tak-toe game" ; 

  function FindWinner(){
    if (  (value[0][0] !== " " && value[0][0] === value[0][1] && value[0][1] === value[0][2]) ||
          (value[1][0] !== " " && value[1][0] === value[1][1] && value[1][1] === value[1][2]) ||
          (value[2][0] !== " " && value[2][0] === value[2][1] && value[2][1] === value[2][2]) ||
          
          (value[0][0] !== " " && value[0][0] === value[1][1] && value[1][1] === value[2][2]) ||
          (value[0][2] !== " " && value[0][2] === value[1][1] && value[2][0] === value[1][1]) ||

          (value[0][0] !== " " && value[0][0] === value[0][1] && value[0][1] === value[0][2]) ||
          (value[0][1] !== " " && value[0][1] === value[1][1] && value[1][1] === value[2][1]) ||
          (value[0][2] !== " " && value[0][2] === value[1][2] && value[1][2] === value[2][2]) 
    ){
      console.log("win")
      labelheader = "GG " + (turn %2 == 0)? "X" : "0"; 
      return true; 
    }
    return false;
  }

  function resetme(){
    setValue( (preValue)=> {
      const restArray = preValue.map( (row, i)=>{
        return row.map((cell, j)=> {
          return " ";
        })
      })
      return restArray;
    })
  }

  return (
    <>
      <div className='space-y-4'>
        <h1 className='text-red-800 text-3xl'>{labelheader}</h1>
        <div className='grid grid-rows-3 gap-2'>
          {value.map( (row, rowIndex) => (
            <div key={rowIndex} className='grid grid-cols-3 gap-2'>
              {row.map( (item, colIndex) => (
                <Square key={colIndex} turn={turn} setTurn={setTurn} value={item} rI={rowIndex} cI={colIndex} setValue={setValue} FindWinner={FindWinner}/>
              ))}
            </div>
          ))}
        </div>
        <button onClick={resetme}>RESET GAME</button>
      </div>
    </>
  )
}


