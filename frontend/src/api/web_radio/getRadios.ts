import api from "../api.ts";
import Radio from "../../types/Radio.ts";

export default async function():Promise<Radio[]> {
    return (await api.get<Radio[]>('/web_radio')).data
}