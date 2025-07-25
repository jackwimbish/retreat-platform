export default ObjectWidget;
/**
 *
 * A JSON data editor widget based on a schema. If you want to represent complex
 * data using a single field, this is the widget to use.
 *
 * If there are multiple field sets, it renders a Tab component with multiple
 * tab panes. Each tab has the title of the fieldset it renders.
 */
declare function ObjectWidget({ block, schema, value, onChange, errors, id, ...props }: {
    [x: string]: any;
    block: any;
    schema: any;
    value: any;
    onChange: any;
    errors?: {};
    id: any;
}): JSX.Element;
declare namespace ObjectWidget {
    namespace propTypes {
        let id: PropTypes.Validator<string>;
        let schema: PropTypes.Validator<object>;
        let errors: PropTypes.Requireable<object>;
        let value: PropTypes.Requireable<object>;
        let onChange: PropTypes.Validator<(...args: any[]) => any>;
    }
    namespace defaultProps {
        let value_1: any;
        export { value_1 as value };
    }
}
import PropTypes from 'prop-types';
