export function View({ className, data, detached, properties, style }: {
    className: any;
    data: any;
    detached: any;
    properties: any;
    style: any;
}): JSX.Element;
export namespace View {
    namespace propTypes {
        let data: PropTypes.Validator<{
            [x: string]: any;
        }>;
    }
}
declare const _default: (props: any) => JSX.Element;
export default _default;
import PropTypes from 'prop-types';
