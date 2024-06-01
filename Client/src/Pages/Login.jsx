import FormLogin from "../components/FormLogin";
import Cookies from "js-cookie"
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constant";

function Login() {
    Cookies.remove(ACCESS_TOKEN)
    Cookies.remove(REFRESH_TOKEN)
    return <FormLogin route="user/login"/>

}

export default Login