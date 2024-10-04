import getRadios from "../../api/web_radio/getRadios.ts";
import {useQuery} from "@tanstack/react-query";
import Radio from "../../types/Radio.ts";

export default function Home(){

    const query = useQuery({ queryKey: ['todos'], queryFn: getRadios })

    return (
        <>
            {query.data && query.data.map((radio: Radio)=> (

              <div>
              {radio.title}{radio.url}
              </div>
            ))
            }

        </>
    )
}